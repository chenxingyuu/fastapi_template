# 角色相关 CRUD 操作
from typing import List

from fastapi import HTTPException, APIRouter
from tortoise.contrib.fastapi import HTTPNotFoundError

from app.system.models import Role, Permission
from app.system.serializers import RolePydantic, RoleCreatePydantic, RoleWithPermissionsPydantic

role_router = APIRouter()


@role_router.post("", summary="创建角色", response_model=RolePydantic)
async def create_role(role: RoleCreatePydantic):
    """
    创建一个新的角色。
    - **role**: 要创建的角色的详细信息。
    """
    role_obj = await Role.create(**role.dict())
    return await RolePydantic.from_tortoise_orm(role_obj)


@role_router.get("", summary="获取角色列表", response_model=List[RolePydantic])
async def list_roles():
    """
    获取所有角色的列表。
    """
    roles = Role.get_queryset().prefetch_related("permissions").all()
    return await RolePydantic.from_queryset(roles)


@role_router.get("/{role_id}", summary="获取角色详细信息", response_model=RoleWithPermissionsPydantic,
                 responses={404: {"model": HTTPNotFoundError}})
async def get_role(role_id: int):
    """
    根据角色 ID 获取单个角色的详细信息。
    - **role_id**: 角色的唯一标识符。
    """
    role = Role.get_queryset().prefetch_related("permissions").get(id=role_id)
    return await RoleWithPermissionsPydantic.from_queryset_single(role)


@role_router.patch(
    "/{role_id}", summary="部分更新角色信息", response_model=RolePydantic, responses={404: {"model": HTTPNotFoundError}}
)
async def patch_role(role_id: int, role: RoleCreatePydantic):
    """
    部分更新指定 ID 角色的信息。
    - **role_id**: 要更新的角色的唯一标识符。
    - **role**: 更新后的角色详细信息（仅更新提供的字段）。
    """
    role_obj = await Role.get_queryset().get_or_none(id=role_id)
    if not role_obj:
        raise HTTPException(status_code=404, detail=f"Role {role_id} not found")

    await Role.get_queryset().filter(id=role_id).update(**role.dict(exclude_unset=True))
    role = Role.get_queryset().get(id=role_id)
    return await RolePydantic.from_queryset_single(role)


@role_router.put("/{role_id}", summary="更新角色信息", response_model=RolePydantic,
                 responses={404: {"model": HTTPNotFoundError}})
async def update_role(role_id: int, role: RoleCreatePydantic):
    """
    更新指定 ID 角色的信息。
    - **role_id**: 要更新的角色的唯一标识符。
    - **role**: 更新后的角色详细信息。
    """
    await Role.get_queryset().filter(id=role_id).update(**role.dict(exclude_unset=True))
    role = Role.get_queryset().get(id=role_id)
    return await RolePydantic.from_queryset_single(role)


@role_router.delete("/{role_id}", summary="删除角色", response_model=dict, responses={404: {"model": HTTPNotFoundError}})
async def delete_role(role_id: int):
    """
    删除指定 ID 的角色。
    - **role_id**: 要删除的角色的唯一标识符。
    """
    deleted_count = await Role.get_queryset().filter(id=role_id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"Role {role_id} not found")
    return {"deleted": deleted_count}


# 角色添加权限
@role_router.post("/{role_id}/permissions", summary="为角色添加权限", response_model=RolePydantic)
async def add_permission_to_role(role_id: int, permission_ids: List[int]):
    """
    为角色添加一个或多个权限。
    - **role_id**: 角色的唯一标识符。
    - **permission_ids**: 要添加的权限的唯一标识符列表。
    """
    role = await Role.get_queryset().get_or_none(id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail=f"Role {role_id} not found")

    permissions = await Permission.get_queryset().filter(id__in=permission_ids).all()
    if len(permissions) != len(permission_ids):
        missing_ids = set(permission_ids) - {permission.id for permission in permissions}
        raise HTTPException(status_code=404, detail=f"Permissions with IDs {missing_ids} not found")

    await role.permissions.add(*permissions)
    return await RolePydantic.from_queryset_single(Role.get_queryset().get(id=role_id))


# 角色删除权限
@role_router.delete("/{role_id}/permissions", summary="删除角色权限", response_model=RolePydantic)
async def delete_permission_from_role(role_id: int, permission_ids: List[int]):
    """
    删除角色的一个或多个权限。
    - **role_id**: 角色的唯一标识符。
    - **permission_ids**: 要删除的权限的唯一标识符列表。
    """
    role = await Role.get_queryset().get_or_none(id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail=f"Role {role_id} not found")

    permissions = await Permission.get_queryset().filter(id__in=permission_ids).all()
    if len(permissions) != len(permission_ids):
        missing_ids = set(permission_ids) - {permission.id for permission in permissions}
        raise HTTPException(status_code=404, detail=f"Permissions with IDs {missing_ids} not found")

    await role.permissions.remove(*permissions)
    return await RolePydantic.from_queryset_single(Role.get_queryset().get(id=role_id))


# 角色修改权限
@role_router.put("/{role_id}/permissions", summary="修改角色权限", response_model=RolePydantic)
async def update_permissions_for_role(role_id: int, permission_ids: List[int]):
    """
    修改角色的权限（覆盖更新）。
    - **role_id**: 角色的唯一标识符。
    - **permission_ids**: 要设置的权限的唯一标识符列表。
    """
    role = await Role.get_queryset().get_or_none(id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail=f"Role {role_id} not found")

    permissions = await Permission.get_queryset().filter(id__in=permission_ids).all()
    if len(permissions) != len(permission_ids):
        missing_ids = set(permission_ids) - {permission.id for permission in permissions}
        raise HTTPException(status_code=404, detail=f"Permissions with IDs {missing_ids} not found")

    await role.permissions.clear()
    await role.permissions.add(*permissions)
    return await RolePydantic.from_queryset_single(Role.get_queryset().get(id=role_id))
