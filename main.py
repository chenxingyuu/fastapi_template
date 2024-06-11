import uvicorn
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from app.system.urls import router as system_router
from cores.config import settings
from cores.model import TORTOISE_ORM

app = FastAPI(title=settings.app.project_name)

app.include_router(system_router, prefix=settings.app.api_version)

register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,
    add_exception_handlers=True,
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
