import subprocess
import threading
import sys
import os
import socket
import time
import urllib.request

from desktop.utils import _decode_line

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if getattr(sys, "frozen", False):
    exe_dir = os.path.dirname(os.path.abspath(sys.executable))
    if os.path.isdir(os.path.join(os.path.dirname(exe_dir), "backend")):
        BASE_DIR = os.path.dirname(exe_dir)
    elif os.path.isdir(os.path.join(exe_dir, "backend")):
        BASE_DIR = exe_dir
elif os.path.isdir(os.path.join(os.getcwd(), "backend")):
    BASE_DIR = os.getcwd()
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
BACKEND_PORT = 8000
FRONTEND_PORT = 5173

_REQUIRED_PACKAGES = ["fastapi", "uvicorn", "sqlalchemy", "pymysql", "pydantic", "cryptography"]


class AppManager:
    def __init__(self):
        self.backend_proc: subprocess.Popen | None = None
        self.frontend_proc: subprocess.Popen | None = None
        self._stop_event = threading.Event()

    @property
    def backend_running(self):
        return self.backend_proc is not None and self.backend_proc.poll() is None

    @property
    def frontend_running(self):
        return self.frontend_proc is not None and self.frontend_proc.poll() is None

    # ── 前置检查 ──────────────────────────────────────────

    def preflight_check(self) -> dict:
        checks = {}
        checks["mysql"] = self._check_mysql()
        checks["port_8000"] = self._check_port(8000)
        checks["port_5173"] = self._check_port(5173)
        checks["nodejs"] = self._check_executable("node", "--version")
        checks["npm"] = self._check_executable("npm", "--version")
        checks["backend_deps"] = self._check_backend_deps()
        checks["frontend_deps"] = os.path.isdir(os.path.join(FRONTEND_DIR, "node_modules"))
        return checks

    def _check_mysql(self) -> bool | str:
        try:
            sys.path.insert(0, BACKEND_DIR)
            from app.config import Config
            import pymysql
            conn = pymysql.connect(
                host=Config.DB_HOST, user=Config.DB_USER,
                password=Config.DB_PASSWORD, port=Config.DB_PORT,
                connect_timeout=3,
            )
            conn.close()
            return True
        except Exception as e:
            return str(e)

    def _check_port(self, port: int) -> bool:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            result = s.connect_ex(("127.0.0.1", port))
            s.close()
            return result != 0
        except Exception:
            return False

    @staticmethod
    def _check_executable(name: str, *args) -> bool | str:
        try:
            cmd = f"{name} {' '.join(args)}" if os.name == "nt" else [name, *args]
            subprocess.run(cmd, capture_output=True, timeout=5, check=False, shell=os.name == "nt")
            return True
        except FileNotFoundError:
            return f"未找到 {name}"
        except Exception as e:
            return str(e)

    def _check_backend_deps(self) -> bool | list:
        missing = []
        for pkg in _REQUIRED_PACKAGES:
            try:
                __import__(pkg)
            except ImportError:
                missing.append(pkg)
        return missing if missing else True

    # ── 健康检查 ──────────────────────────────────────────

    @staticmethod
    def health_check(url: str, retries: int = 12, interval: float = 1) -> bool:
        for _ in range(retries):
            try:
                r = urllib.request.urlopen(url, timeout=3)
                if r.status == 200:
                    return True
            except Exception:
                time.sleep(interval)
        return False

    # ── 依赖安装 ──────────────────────────────────────────

    def install_backend_deps(self, log_callback) -> bool:
        req_file = os.path.join(BACKEND_DIR, "requirements", "prod.txt")
        if not os.path.isfile(req_file):
            log_callback("[后端] 未找到 requirements/prod.txt")
            return False
        log_callback("[后端] 正在安装 Python 依赖 ...")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", req_file],
                capture_output=True, text=True, timeout=120,
            )
            if result.returncode == 0:
                log_callback("[后端] 依赖安装完成")
                return True
            log_callback(f"[后端] 依赖安装失败:\n{result.stderr.strip()}")
            return False
        except subprocess.TimeoutExpired:
            log_callback("[后端] 依赖安装超时(>120s)")
            return False
        except Exception as e:
            log_callback(f"[后端] 依赖安装出错: {e}")
            return False

    # ── 启动 / 停止 ──────────────────────────────────────

    def start_backend(self, log_callback):
        if self.backend_running:
            log_callback("[后端] 已在运行中")
            return
        self._stop_event.clear()
        missing = self._check_backend_deps()
        if isinstance(missing, list):
            log_callback(f"[后端] 缺少依赖: {', '.join(missing)}，正在自动安装 ...")
            if not self.install_backend_deps(log_callback):
                log_callback("[后端] 依赖安装失败，请手动执行: pip install -r backend/requirements/prod.txt")
                return
        if not self._check_mysql():
            log_callback("[后端] ⚠ MySQL 不可用，启动后可能无法连接数据库")
        log_callback("[后端] 正在启动 ...")
        try:
            self.backend_proc = subprocess.Popen(
                [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", str(BACKEND_PORT)],
                cwd=BACKEND_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            )
            threading.Thread(target=self._pipe_log, args=(self.backend_proc, "[后端]", log_callback), daemon=True).start()
            log_callback(f"[后端] 进程ID {self.backend_proc.pid}，正在健康检查 ...")
            ok = self.health_check(f"http://127.0.0.1:{BACKEND_PORT}/api/categories")
            if ok:
                log_callback(f"[后端] ✅ 已就绪 (http://localhost:{BACKEND_PORT})")
            else:
                log_callback("[后端] ⚠ 启动似乎异常，请检查日志")
        except Exception as e:
            log_callback(f"[后端] 启动失败: {e}")

    def start_frontend(self, log_callback):
        if self.frontend_running:
            log_callback("[前端] 已在运行中")
            return
        if not os.path.isdir(os.path.join(FRONTEND_DIR, "node_modules")):
            log_callback("[前端] 正在安装依赖 ...")
            try:
                subprocess.run("npm install", cwd=FRONTEND_DIR, check=True,
                               shell=True, capture_output=True, timeout=120)
                log_callback("[前端] 依赖安装完成")
            except subprocess.TimeoutExpired:
                log_callback("[前端] npm install 超时")
                return
            except subprocess.CalledProcessError as e:
                err_text = _decode_line(e.stderr) if isinstance(e.stderr, bytes) else str(e.stderr)
                log_callback(f"[前端] 依赖安装失败:\n{err_text}")
                return
            except FileNotFoundError:
                log_callback("[前端] 未找到 npm，请确认已安装 Node.js")
                return
        log_callback("[前端] 正在启动 ...")
        try:
            self.frontend_proc = subprocess.Popen(
                "npx vite --host",
                cwd=FRONTEND_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                shell=True,
            )
            threading.Thread(target=self._pipe_log, args=(self.frontend_proc, "[前端]", log_callback), daemon=True).start()
            log_callback(f"[前端] 进程ID {self.frontend_proc.pid}")
            time.sleep(2)
            if self.frontend_running:
                log_callback(f"[前端] ✅ 已就绪 (http://localhost:{FRONTEND_PORT})")
        except Exception as e:
            log_callback(f"[前端] 启动失败: {e}")

    # ── 停止 ──────────────────────────────────────────────

    @staticmethod
    def _kill_tree(pid: int):
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)], capture_output=True)

    def stop_backend(self, log_callback):
        if not self.backend_running:
            log_callback("[后端] 未在运行")
            return
        pid = self.backend_proc.pid
        self._kill_tree(pid)
        try:
            self.backend_proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            self.backend_proc.kill()
        self.backend_proc = None
        log_callback(f"[后端] PID {pid} 已终止")

    def stop_frontend(self, log_callback):
        if not self.frontend_running:
            log_callback("[前端] 未在运行")
            return
        pid = self.frontend_proc.pid
        self._kill_tree(pid)
        try:
            self.frontend_proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            self.frontend_proc.kill()
        self.frontend_proc = None
        log_callback(f"[前端] PID {pid} 已终止")

    def stop_all(self, log_callback):
        self._stop_event.set()
        threads = []
        if self.frontend_running:
            t = threading.Thread(target=self.stop_frontend, args=(log_callback,), daemon=True)
            t.start()
            threads.append(t)
        if self.backend_running:
            t = threading.Thread(target=self.stop_backend, args=(log_callback,), daemon=True)
            t.start()
            threads.append(t)
        for t in threads:
            t.join(timeout=3)
        self.kill_by_port(BACKEND_PORT, log_callback)
        self.kill_by_port(FRONTEND_PORT, log_callback)
        log_callback("全部服务已停止")

    # ── 日志管道 ──────────────────────────────────────────

    def _pipe_log(self, proc, prefix, log_callback):
        try:
            for line in iter(proc.stdout.readline, b""):
                if self._stop_event.is_set():
                    break
                if line:
                    text = _decode_line(line)
                    log_callback(f"{prefix} {text}")
        except Exception:
            pass

    # ── 端口清理 ──────────────────────────────────────────

    @staticmethod
    def kill_by_port(port, log_callback):
        try:
            result = subprocess.run(["netstat", "-ano"], capture_output=True)
            out = _decode_line(result.stdout) if isinstance(result.stdout, bytes) else result.stdout
            for line in out.splitlines():
                if f":{port}" in line and "LISTENING" in line:
                    parts = line.strip().split()
                    pid = parts[-1]
                    subprocess.run(["taskkill", "/PID", pid, "/F"], capture_output=True)
                    log_callback(f"已终止端口 {port} 上的进程 {pid}")
        except Exception as e:
            log_callback(f"端口清理出错: {e}")