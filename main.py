import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise

from app.system.urls import router as system_router
from cores.config import settings
from cores.model import TORTOISE_ORM

app = FastAPI(
    title=settings.app.project_name,
    debug=settings.app.debug,
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头部
)

# 添加路由
app.include_router(system_router, prefix=settings.app.api_version)

register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=False,
    add_exception_handlers=True,
)

if __name__ == "__main__":
    uvicorn.run(app, host=settings.app.host, port=settings.app.port)
