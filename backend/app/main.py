from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.routes import notes, ai, auth
from app.routes import upload
from app.websocket.handlers import websocket_endpoint
from fastapi.staticfiles import StaticFiles
import os

# 初始化数据库
init_db()

app = FastAPI(title="AI笔记应用 API", version="1.0.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api")
app.include_router(notes.router, prefix="/api")
app.include_router(ai.router, prefix="/api")
app.include_router(upload.router)

# 静态文件（图片上传）
static_dir = os.path.join(os.getcwd(), "data", "uploads")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static/uploads", StaticFiles(directory=static_dir), name="uploads")

# WebSocket路由
@app.websocket("/ws")
async def websocket_route(websocket: WebSocket):
    # 从查询参数获取note_id（可选）
    note_id = websocket.query_params.get("note_id")
    await websocket_endpoint(websocket, note_id)


@app.get("/")
async def root():
    return {"message": "AI笔记应用 API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "ok"}

