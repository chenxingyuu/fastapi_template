from typing import List

from fastapi import APIRouter, Depends, HTTPException, Security
from tortoise.contrib.fastapi import HTTPNotFoundError
from tortoise.exceptions import DoesNotExist

from app.system.filters import ListRoleFilterSet
from app.system.models import Permission, Role
from app.system.serializers import (
    PermissionDetail,
    RoleCreate,
    RoleDetail,
    RolePatch,
    RoleUpdate,
)
from app.system.views.auth import get_current_active_user
from cores.paginate import PageModel, PaginationParams, paginate
from cores.response import ResponseModel

role_router = APIRouter()
role_permission_router = APIRouter()


@role_router.post(
    "",
    summary="创建角色",
    response_model=ResponseModel[RoleDetail],
    dependencies=[
        Security(get_current_active_user, scopes=["system:role:create"])
    ],
)
async def create_role(role: RoleCreate):
    """
    创建一个新的角色。
    - **role**: 要创建的角色的详细信息。
    """
    role_obj = await Role.create(**role.dict())
    response = await RoleDetail.from_tortoise_orm(role_obj)
    return ResponseModel(data=response)


@role_router.get(
    "",
    summary="获取角色列表",
    response_model=ResponseModel[PageModel[RoleDetail]],
    dependencies=[
        Security(get_current_active_user, scopes=["system:role:read"])
    ],
)
async def list_roles(
    role_filter: ListRoleFilterSet = Depends(),
    pagination: PaginationParams = Depends(),
):
    """
    获取所有角色的列表。
    """
    query = role_filter.apply_filters()
    page_data = await paginate(query, pagination, RoleDetail)
    return ResponseModel(data=page_data)


@role_router.get(
    "/all",
    summary="获取所有角色列表",
    response_model=ResponseModel[List[RoleDetail]],
    dependencies=[
        Security(get_current_active_user, scopes=["system:role:read"])
    ],
)
async def list_roles(
    role_filter: ListRoleFilterSet = Depends(),
):
    """
    获取所有角色的列表。
    """
    query = role_filter.apply_filters()
    role_data = await RoleDetail.from_queryset(query)
    return ResponseModel(data=role_data)


@role_router.get(
    "/{role_id}",
    summary="获取角色详细信息",
    response_model=ResponseModel[RoleDetail],
    responses={404: {"model": HTTPNotFoundError}},
    dependencies=[
        Security(get_current_active_user, scopes=["system:role:read"])
    ],
)
async def get_role(role_id: int):
    """
    根据角色 ID 获取单个角色的详细信息。
    - **role_id**: 角色的唯一标识符。
    """
    try:
        role_queryset = Role.get_queryset().get(id=role_id)
        response = await RoleDetail.from_queryset_single(role_queryset)
        return ResponseModel(data=response)
    except DoesNotExist:
        raise HTTPException(
            status_code=404, detail=f"Role {role_id} not found"
        )


@role_router.patch(
    "/{role_id}",
    summary="部分更新角色信息",
    response_model=ResponseModel[RoleDetail],
    responses={404: {"model": HTTPNotFoundError}},
    dependencies=[
        Security(get_current_active_user, scopes=["system:role:update"])
    ],
)
async def patch_role(role_id: int, role: RolePatch):
    """
    部分更新指定 ID 角色的信息。
    - **role_id**: 要更新的角色的唯一标识符。
    - **role**: 更新后的角色详细信息（仅更新提供的字段）。
    """
    role_obj = await Role.get_queryset().get_or_none(id=role_id)
    if not role_obj:
        raise HTTPException(
            status_code=404, detail=f"Role {role_id} not found"
        )

    await Role.get_queryset().filter(id=role_id).update(
        **role.dict(exclude_unset=True)
    )
    updated_role = Role.get_queryset().get(id=role_id)
    response = await RoleDetail.from_queryset_single(updated_role)
    return ResponseModel(data=response)


@role_router.put(
    "/{role_id}",
    summary="更新角色信息",
    response_model=ResponseModel[RoleDetail],
    responses={404: {"model": HTTPNotFoundError}},
    dependencies=[
        Security(get_current_active_user, scopes=["system:role:update"])
    ],
)
async def update_role(role_id: int, role: RoleUpdate):
    """
    更新指定 ID 角色的信息。
    - **role_id**: 要更新的角色的唯一标识符。
    - **role**: 更新后的角色详细信息。
    """
    role_obj = await Role.get_queryset().get_or_none(id=role_id)
    if not role_obj:
        raise HTTPException(
            status_code=404, detail=f"Role {role_id} not found"
        )

    await Role.get_queryset().filter(id=role_id).update(
        **role.dict(exclude_unset=True)
    )
    updated_role = Role.get_queryset().get(id=role_id)
    response = await RoleDetail.from_queryset_single(updated_role)
    return ResponseModel(data=response)


@role_router.delete(
    "/{role_id}",
    summary="删除角色",
    response_model=ResponseModel[dict],
    responses={404: {"model": HTTPNotFoundError}},
    dependencies=[
        Security(get_current_active_user, scopes=["system:role:delete"])
    ],
)
async def delete_role(role_id: int):
    """
    删除指定 ID 的角色。
    - **role_id**: 要删除的角色的唯一标识符。
    """
    deleted_count = await Role.get_queryset().filter(id=role_id).delete()
    if not deleted_count:
        raise HTTPException(
            status_code=404, detail=f"Role {role_id} not found"
        )
    return ResponseModel(data={"deleted": deleted_count})


@role_permission_router.get(
    "/{role_id}/permissions",
    summary="角色的权限列表",
    response_model=ResponseModel[List[PermissionDetail]],
    responses={404: {"model": HTTPNotFoundError}},
    dependencies=[
        Security(
            get_current_active_user,
            scopes=["system:role:read", "system:permission:read"],
        )
    ],
)
async def get_role_permissions(role_id: int):
    """
    根据角色 ID 获取单个角色的权限列表。
    - **role_id**: 角色的唯一标识符。
    """
    role = (
        await Role.get_queryset()
        .prefetch_related("permissions")
        .get_or_none(id=role_id)
    )
    if not role:
        return ResponseModel(code=404, msg=f"Role {role} not found")

    permissions_data = await PermissionDetail.from_queryset(
        role.permissions.all()
    )
    return ResponseModel(data=permissions_data)


@role_permission_router.post(
    "/{role_id}/permissions",
    summary="为角色添加权限",
    response_model=ResponseModel[RoleDetail],
    dependencies=[
        Security(
            get_current_active_user,
            scopes=["system:role:update", "system:permission:read"],
        )
    ],
)
async def add_permission_to_role(role_id: int, permission_ids: List[int]):
    """
    为角色添加一个或多个权限。
    - **role_id**: 角色的唯一标识符。
    - **permission_ids**: 要添加的权限的唯一标识符列表。
    """
    role = await Role.get_queryset().get_or_none(id=role_id)
    if not role:
        raise HTTPException(
            status_code=404, detail=f"Role {role_id} not found"
        )

    permissions = (
        await Permission.get_queryset().filter(id__in=permission_ids).all()
    )
    if len(permissions) != len(permission_ids):
        missing_ids = set(permission_ids) - {
            permission.id for permission in permissions
        }
        raise HTTPException(
            status_code=404,
            detail=f"Permissions with IDs {missing_ids} not found",
        )

    await role.permissions.add(*permissions)
    updated_role = Role.get_queryset().get(id=role_id)
    response = await RoleDetail.from_queryset_single(updated_role)
    return ResponseModel(data=response)


@role_permission_router.delete(
    "/{role_id}/permissions",
    summary="删除角色权限",
    response_model=ResponseModel[RoleDetail],
    dependencies=[
        Security(
            get_current_active_user,
            scopes=["system:role:update", "system:permission:read"],
        )
    ],
)
async def delete_permission_from_role(role_id: int, permission_ids: List[int]):
    """
    删除角色的一个或多个权限。
    - **role_id**: 角色的唯一标识符。
    - **permission_ids**: 要删除的权限的唯一标识符列表。
    """
    role = await Role.get_queryset().get_or_none(id=role_id)
    if not role:
        raise HTTPException(
            status_code=404, detail=f"Role {role_id} not found"
        )

    permissions = (
        await Permission.get_queryset().filter(id__in=permission_ids).all()
    )
    if len(permissions) != len(permission_ids):
        missing_ids = set(permission_ids) - {
            permission.id for permission in permissions
        }
        raise HTTPException(
            status_code=404,
            detail=f"Permissions with IDs {missing_ids} not found",
        )

    await role.permissions.remove(*permissions)
    updated_role = await Role.get_queryset().get(id=role_id)
    response = await RoleDetail.from_queryset_single(updated_role)
    return ResponseModel(data=response)


@role_permission_router.put(
    "/{role_id}/permissions",
    summary="修改角色权限",
    response_model=ResponseModel[RoleDetail],
    dependencies=[
        Security(
            get_current_active_user,
            scopes=["system:role:update", "system:permission:read"],
        )
    ],
)
async def update_permissions_for_role(role_id: int, permission_ids: List[int]):
    """
    修改角色的权限（覆盖更新）。
    - **role_id**: 角色的唯一标识符。
    - **permission_ids**: 要设置的权限的唯一标识符列表。
    """
    role = await Role.get_queryset().get_or_none(id=role_id)
    if not role:
        raise HTTPException(
            status_code=404, detail=f"Role {role_id} not found"
        )

    permissions = (
        await Permission.get_queryset().filter(id__in=permission_ids).all()
    )
    if len(permissions) != len(permission_ids):
        missing_ids = set(permission_ids) - {
            permission.id for permission in permissions
        }
        raise HTTPException(
            status_code=404,
            detail=f"Permissions with IDs {missing_ids} not found",
        )

    await role.permissions.clear()
    await role.permissions.add(*permissions)
    updated_role = Role.get_queryset().get(id=role_id)
    response = await RoleDetail.from_queryset_single(updated_role)
    return ResponseModel(data=response)
