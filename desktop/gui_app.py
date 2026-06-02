import customtkinter as ctk
import threading
import webbrowser

from desktop.app_manager import AppManager, BACKEND_PORT, FRONTEND_PORT

_CHECK_LABELS = {
    "mysql": "MySQL",
    "port_8000": "端口 8000",
    "port_5173": "端口 5173",
    "nodejs": "Node.js",
    "npm": "npm",
    "backend_deps": "Python 依赖",
    "frontend_deps": "前端依赖",
}


class DevGUI:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.mgr = AppManager()

        self.root = ctk.CTk()
        self.root.title("个人记账本 - 开发启动器")
        self.root.geometry("960x600")
        self.root.minsize(900, 520)
        self.root.resizable(True, True)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(3, weight=1)

        self._check_results = {}
        self._progress_animating = False
        self._build_header()
        self._build_check_panel()
        self._build_controls()
        self._build_progress()
        self._build_log()
        self._build_status_bar()

        self._update_status()
        self._center_window()
        self._run_preflight()

    def _build_header(self):
        frame = ctk.CTkFrame(self.root, fg_color="transparent", corner_radius=0)
        frame.grid(row=0, column=0, sticky="ew", padx=0, pady=(8, 0))
        frame.columnconfigure(1, weight=1)

        title = ctk.CTkLabel(
            frame, text="\U0001f4ca  个人记账本",
            font=("Microsoft YaHei", 18, "bold"),
            text_color="#60a5fa",
        )
        title.grid(row=0, column=0, padx=(24, 10), pady=(6, 2), sticky="w")

        self.backend_label = ctk.CTkLabel(
            frame, text="", font=("Consolas", 11),
        )
        self.backend_label.grid(row=0, column=1, padx=5, sticky="e")

        self.frontend_label = ctk.CTkLabel(
            frame, text="", font=("Consolas", 11),
        )
        self.frontend_label.grid(row=0, column=2, padx=(5, 24), sticky="e")

    def _build_check_panel(self):
        frame = ctk.CTkFrame(self.root, fg_color="transparent", corner_radius=0)
        frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(4, 0))
        frame.columnconfigure(0, weight=1)

        header = ctk.CTkLabel(
            frame, text="\U0001f50d 环境检查", anchor="w",
            font=("Microsoft YaHei", 11, "bold"), text_color="#888",
        )
        header.grid(row=0, column=0, sticky="w", pady=(0, 4))

        inner = ctk.CTkFrame(frame, fg_color="#2a2a2a", corner_radius=8)
        inner.grid(row=1, column=0, sticky="ew")
        inner.columnconfigure(list(range(7)), weight=1)

        self._check_items = {}
        for i, key in enumerate(_CHECK_LABELS):
            card = ctk.CTkFrame(inner, fg_color="#333", corner_radius=6, height=56)
            card.grid(row=0, column=i, padx=4, pady=6, sticky="ew")
            card.grid_propagate(False)

            icon = ctk.CTkLabel(card, text="\u23f3", font=("Segoe UI Emoji", 16))
            icon.pack(pady=(6, 0))

            label = ctk.CTkLabel(card, text=_CHECK_LABELS[key], font=("Microsoft YaHei", 10), text_color="#888")
            label.pack()

            self._check_items[key] = icon

    def _build_controls(self):
        frame = ctk.CTkFrame(self.root, fg_color="transparent", corner_radius=0)
        frame.grid(row=2, column=0, sticky="ew", padx=0, pady=(2, 0))
        frame.columnconfigure(0, weight=1)

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(6, 6))

        self.btn_start_all = ctk.CTkButton(
            btn_frame, text="\u25b6  全部启动",
            fg_color="#22c55e", hover_color="#16a34a",
            text_color="white", width=120, height=32,
            font=("Microsoft YaHei", 12, "bold"),
            command=self._start_all,
        )
        self.btn_start_all.pack(side="left", padx=(0, 4))

        self.btn_stop_all = ctk.CTkButton(
            btn_frame, text="\u25a0  全部停止",
            fg_color="#ef4444", hover_color="#dc2626",
            text_color="white", width=120, height=32,
            font=("Microsoft YaHei", 12, "bold"),
            command=self._stop_all,
        )
        self.btn_stop_all.pack(side="left", padx=4)

        ctk.CTkFrame(btn_frame, width=2, height=28, fg_color="#444").pack(
            side="left", padx=10, fill="y")

        self.btn_start_be = ctk.CTkButton(
            btn_frame, text="\u25b6  启动后端",
            fg_color="#3b82f6", hover_color="#2563eb",
            text_color="white", width=105, height=30,
            font=("Microsoft YaHei", 11),
            command=lambda: self._run_in_thread(self.mgr.start_backend),
        )
        self.btn_start_be.pack(side="left", padx=3)

        self.btn_stop_be = ctk.CTkButton(
            btn_frame, text="\u25a0  停止后端",
            fg_color="#6366f1", hover_color="#4f46e5",
            text_color="white", width=105, height=30,
            font=("Microsoft YaHei", 11),
            command=lambda: self._run_in_thread(self.mgr.stop_backend),
        )
        self.btn_stop_be.pack(side="left", padx=3)

        ctk.CTkFrame(btn_frame, width=2, height=28, fg_color="#444").pack(
            side="left", padx=10, fill="y")

        self.btn_start_fe = ctk.CTkButton(
            btn_frame, text="\u25b6  启动前端",
            fg_color="#3b82f6", hover_color="#2563eb",
            text_color="white", width=105, height=30,
            font=("Microsoft YaHei", 11),
            command=lambda: self._run_in_thread(self.mgr.start_frontend),
        )
        self.btn_start_fe.pack(side="left", padx=3)

        self.btn_stop_fe = ctk.CTkButton(
            btn_frame, text="\u25a0  停止前端",
            fg_color="#6366f1", hover_color="#4f46e5",
            text_color="white", width=105, height=30,
            font=("Microsoft YaHei", 11),
            command=lambda: self._run_in_thread(self.mgr.stop_frontend),
        )
        self.btn_stop_fe.pack(side="left", padx=3)

        ctk.CTkFrame(btn_frame, width=2, height=28, fg_color="#444").pack(
            side="left", padx=10, fill="y")

        link_color = "#60a5fa"
        link_font = ("Microsoft YaHei", 10)

        be_link = ctk.CTkLabel(
            btn_frame, text="后端API", font=link_font,
            text_color=link_color, cursor="hand2",
        )
        be_link.pack(side="left", padx=5)
        be_link.bind("<Button-1>", lambda e: webbrowser.open(
            f"http://localhost:{BACKEND_PORT}"))

        docs_link = ctk.CTkLabel(
            btn_frame, text="接口文档", font=link_font,
            text_color=link_color, cursor="hand2",
        )
        docs_link.pack(side="left", padx=5)
        docs_link.bind("<Button-1>", lambda e: webbrowser.open(
            f"http://localhost:{BACKEND_PORT}/docs"))

        fe_link = ctk.CTkLabel(
            btn_frame, text="前端页面", font=link_font,
            text_color=link_color, cursor="hand2",
        )
        fe_link.pack(side="left", padx=5)
        fe_link.bind("<Button-1>", lambda e: webbrowser.open(
            f"http://localhost:{FRONTEND_PORT}"))

    def _build_progress(self):
        self._progress = ctk.CTkProgressBar(
            self.root, height=4, corner_radius=2,
            fg_color="#333", progress_color="#22c55e",
        )
        self._progress.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 0))
        self._progress.set(0)

    def _build_log(self):
        frame = ctk.CTkFrame(self.root, corner_radius=10)
        frame.grid(row=4, column=0, sticky="nsew", padx=20, pady=(6, 10))
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        self.log = ctk.CTkTextbox(
            frame, font=("Consolas", 11),
            fg_color="#1e1e2e", text_color="#cdd6f4",
            corner_radius=8, wrap="word",
            border_width=0,
        )
        self.log.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)

        self.log.tag_config("info", foreground="#cdd6f4")
        self.log.tag_config("warn", foreground="#f9e2af")
        self.log.tag_config("err", foreground="#f38ba8")
        self.log.tag_config("ok", foreground="#a6e3a1")

    def _build_status_bar(self):
        self.status_var = ctk.StringVar(value="就绪")
        bar = ctk.CTkLabel(
            self.root, textvariable=self.status_var,
            anchor="w", font=("Microsoft YaHei", 10),
            fg_color="#2d2d2d", text_color="#888",
            corner_radius=0,
        )
        bar.grid(row=5, column=0, sticky="ew", padx=0, pady=0)

    # ── 前置检查 ──────────────────────────────────────────

    def _run_preflight(self):
        self._log("正在检查环境 ...")
        t = threading.Thread(target=self._do_preflight, daemon=True)
        t.start()

    def _do_preflight(self):
        results = self.mgr.preflight_check()
        self.root.after(0, self._show_preflight, results)

    def _show_preflight(self, results):
        self._check_results = results
        all_pass = True
        for key, value in results.items():
            icon = self._check_items[key]
            if value is True:
                icon.configure(text="\u2705", text_color="#22c55e")
            else:
                icon.configure(text="\u274c", text_color="#ef4444")
                if key == "backend_deps":
                    self._log(f"[检查] Python 缺少依赖: {', '.join(value)}")
                elif key == "frontend_deps":
                    self._log("[检查] 前端依赖未安装 (node_modules 不存在)")
                else:
                    self._log(f"[检查] {_CHECK_LABELS[key]}: {value}")
                all_pass = False
        if all_pass:
            self._log("\u2705 环境检查全部通过")

    # ── 进度条 ──────────────────────────────────────────

    def _show_progress(self, active: bool):
        if active:
            self._progress_animating = True
            self._progress.configure(progress_color="#22c55e")
            self._progress.set(0.3)
            self._tick_progress()
        else:
            self._progress_animating = False
            self._progress.set(1)
            self.root.after(500, lambda: self._progress.set(0) if not self._progress_animating else None)

    def _tick_progress(self):
        if not self._progress_animating:
            return
        v = self._progress.get()
        self._progress.set(v + 0.06 if v < 0.8 else 0.3)
        self.root.after(200, self._tick_progress)

    # ── 工具 ──────────────────────────────────────────

    def _center_window(self):
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - 960) // 2
        y = (sh - 600) // 2
        self.root.geometry(f"960x600+{x}+{y}")

    def _log(self, msg: str):
        if not msg:
            return
        self.root.after(0, self._append_log, msg)

    def _append_log(self, msg: str):
        tag = "info"
        if any(kw in msg for kw in ("错误", "失败", "强制终止", "出错")):
            tag = "err"
        elif any(kw in msg for kw in ("警告", "超时")):
            tag = "warn"
        elif any(kw in msg for kw in ("就绪", "运行中", "已启动", "已终止", "已停止", "进程ID", "\u2705", "\u25b6")):
            tag = "ok"

        self.log.configure(state="normal")
        self.log.insert("end", msg + "\n", tag)
        self.log.see("end")
        self.log.configure(state="disabled")

    def _update_status(self):
        be = "运行中" if self.mgr.backend_running else "已停止"
        fe = "运行中" if self.mgr.frontend_running else "已停止"

        be_color = "#4ade80" if self.mgr.backend_running else "#f87171"
        fe_color = "#4ade80" if self.mgr.frontend_running else "#f87171"

        self.backend_label.configure(text=f"\u25cf {be}", text_color=be_color)
        self.frontend_label.configure(text=f"\u25cf {fe}", text_color=fe_color)
        self.status_var.set(f"后端: {be}  |  前端: {fe}")

        self.root.after(1000, self._update_status)

    def _run_in_thread(self, func):
        self._show_progress(True)
        t = threading.Thread(target=self._run_and_finish, args=(func,), daemon=True)
        t.start()

    def _run_and_finish(self, func):
        try:
            func(self._log)
        finally:
            self.root.after(200, lambda: self._show_progress(False))

    def _start_all(self):
        self._run_in_thread(self.mgr.start_backend)
        self._run_in_thread(self.mgr.start_frontend)

    def _stop_all(self):
        self._run_in_thread(self.mgr.stop_all)

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.mainloop()

    def _on_close(self):
        self._progress_animating = False
        self._log("正在关闭服务 ...")
        self._close_started = True
        self._close_elapsed = 0
        threading.Thread(target=self.mgr.stop_all, args=(lambda _: None,), daemon=True).start()
        self._poll_shutdown()

    def _poll_shutdown(self):
        be = self.mgr.backend_running
        fe = self.mgr.frontend_running
        self._close_elapsed += 1
        if not be and not fe:
            self._log("服务已全部关闭")
            self.root.destroy()
            return
        if self._close_elapsed > 12:
            self._log("等待超时，强制关闭窗口")
            self.root.destroy()
            return
        self.root.after(500, self._poll_shutdown)