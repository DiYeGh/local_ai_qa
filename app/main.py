from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import upload_router, qa_router
from app.config.settings import settings

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    description="基于FastAPI、Milvus和Ollama的本地知识库AI问答系统",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(
    upload_router.router,
    prefix=settings.API_V1_STR,
    tags=["文档管理"]
)

app.include_router(
    qa_router.router,
    prefix=settings.API_V1_STR,
    tags=["问答系统"]
)

@app.get("/")
async def root():
    """
    根路由，返回系统信息
    """
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """
    健康检查接口
    """
    return {
        "status": "healthy"
    }
