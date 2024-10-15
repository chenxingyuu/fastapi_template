from fastapi import APIRouter

from cores.response import ResponseModel

common_router = APIRouter()


@common_router.post(
    "/healthy",
    summary="healthy",
    response_model=ResponseModel,
)
async def healthy():
    return ResponseModel()
