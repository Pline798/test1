from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import engine, Base
from app.routers import categories, transactions, stats
from app.init_db import init_seed_categories

import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    init_seed_categories()
    yield


app = FastAPI(title="个人记账本 API", version="1.0.0", lifespan=lifespan)

# 挂载项目文档目录（供前端页面在线浏览 Markdown 文档）
_docs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "docs")
if os.path.isdir(_docs_dir):
    app.mount("/docs", StaticFiles(directory=_docs_dir), name="docs")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(categories.router)
app.include_router(transactions.router)
app.include_router(stats.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)