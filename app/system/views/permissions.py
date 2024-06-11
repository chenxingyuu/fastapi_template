import datetime
from typing import List

from fastapi import APIRouter, HTTPException
from tortoise.contrib.fastapi import HTTPNotFoundError
from tortoise.exceptions import DoesNotExist

from app.system.models import Permission
from app.system.serializers import (
    PermissionCreatePydantic,
    PermissionPydantic,
)

permission_router = APIRouter()


# 用户相关 CRUD 操作


# 权限相关 CRUD 操作
@permission_router.post("", summary="创建权限", response_model=PermissionPydantic)
async def create_permission(permission: PermissionCreatePydantic):
    """
    创建一个新的权限。
    - **permission**: 要创建的权限的详细信息。
    """
    permission_obj = await Permission.create(**permission.dict())
    return await PermissionPydantic.from_tortoise_orm(permission_obj)


@permission_router.get("", summary="获取权限列表", response_model=List[PermissionPydantic])
async def list_permissions():
    """
    获取所有权限的列表。
    """
    permissions = Permission.get_queryset().all()
    return await PermissionPydantic.from_queryset(permissions)


@permission_router.get(
    "/{permission_id}", summary="获取权限详细信息", response_model=PermissionPydantic,
    responses={404: {"model": HTTPNotFoundError}}
)
async def get_permission(permission_id: int):
    """
    根据权限 ID 获取单个权限的详细信息。
    - **permission_id**: 权限的唯一标识符。
    """
    permission = Permission.get_queryset().get(id=permission_id)
    return await PermissionPydantic.from_queryset_single(permission)


@permission_router.put(
    "/{permission_id}", summary="更新权限信息", response_model=PermissionPydantic,
    responses={404: {"model": HTTPNotFoundError}}
)
async def update_permission(permission_id: int, permission: PermissionCreatePydantic):
    """
    更新指定 ID 权限的信息。
    - **permission_id**: 要更新的权限的唯一标识符。
    - **permission**: 更新后的权限详细信息。
    """
    permission_obj = await Permission.get_queryset().get_or_none(id=permission_id)
    if not permission_obj:
        raise HTTPException(status_code=404, detail=f"Permission {permission_id} not found")

    await Permission.get_queryset().filter(id=permission_id).update(**permission.dict(exclude_unset=True))
    permission = Permission.get_queryset().get(id=permission_id)
    return await PermissionPydantic.from_queryset_single(permission)


@permission_router.patch(
    "/{permission_id}", summary="部分更新权限信息", response_model=PermissionPydantic,
    responses={404: {"model": HTTPNotFoundError}}
)
async def patch_permission(permission_id: int, permission: PermissionCreatePydantic):
    """
    部分更新指定 ID 权限的信息。
    - **permission_id**: 要更新的权限的唯一标识符。
    - **permission**: 更新后的权限详细信息（仅更新提供的字段）。
    """
    permission_obj = await Permission.get_queryset().get_or_none(id=permission_id)
    if not permission_obj:
        raise HTTPException(status_code=404, detail=f"Permission {permission_id} not found")

    await Permission.get_queryset().filter(id=permission_id).update(**permission.dict(exclude_unset=True))
    permission = Permission.get_queryset().get(id=permission_id)
    return await PermissionPydantic.from_queryset_single(permission)


@permission_router.delete(
    "/{permission_id}", summary="删除权限", response_model=dict, responses={404: {"model": HTTPNotFoundError}}
)
async def delete_permission(permission_id: int):
    """
    逻辑删除指定 ID 的权限。
    - **permission_id**: 要删除的权限的唯一标识符。
    """
    try:
        permission = await Permission.get_queryset().get(id=permission_id)
        # 更新 deleted_at 字段以标记删除
        permission.deleted_at = datetime.datetime.now()
        await permission.save()
        return {"deleted": 1}
    except DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Permission {permission_id} not found")
