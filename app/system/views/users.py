import secrets
import string
from typing import Optional, List

from fastapi import APIRouter, Query, HTTPException
from tortoise.contrib.fastapi import HTTPNotFoundError

from app.system.models import User, Role, Permission
from app.system.serializers import UserPydantic, UserCreatePydantic, UserUpdatePydantic, RolePydantic, PermissionPydantic

user_router = APIRouter()


def generate_password(length: int = 12) -> str:
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password


@user_router.post(path="", summary="创建用户", response_model=UserPydantic)
async def create_user(user: UserCreatePydantic):
    """
    创建一个新的系统用户。
    - **user**: 要创建的用户的详细信息。
    """
    password = generate_password(12)
    user_obj = await User.create(**user.dict(exclude_unset=True), hashed_password=password)
    return await UserPydantic.from_tortoise_orm(user_obj)


@user_router.get("", summary="获取用户列表", response_model=List[UserPydantic])
async def list_user(
    username: Optional[str] = Query(None, description="按用户名过滤"),
    email: Optional[str] = Query(None, description="按电子邮件过滤"),
    is_active: Optional[bool] = Query(None, description="按是否激活状态过滤"),
    is_superuser: Optional[bool] = Query(None, description="按超级用户状态过滤"),
):
    """
    获取系统用户列表，支持多种过滤条件。
    - **username**: 用户名过滤条件（模糊匹配）。
    - **email**: 电子邮件过滤条件（模糊匹配）。
    - **is_active**: 是否激活过滤条件。
    - **is_superuser**: 是否超级用户过滤条件。
    """
    filters = {}
    if username is not None:
        filters["username__icontains"] = username
    if email is not None:
        filters["email__icontains"] = email
    if is_active is not None:
        filters["is_active"] = is_active
    if is_superuser is not None:
        filters["is_superuser"] = is_superuser

    users = User.get_queryset().filter(**filters)
    return await UserPydantic.from_queryset(users)


@user_router.get("/{user_id}", summary="获取用户详细信息", response_model=UserPydantic,
                 responses={404: {"model": HTTPNotFoundError}})
async def get_user(user_id: int):
    """
    根据用户 ID 获取单个用户的详细信息。
    - **user_id**: 用户的唯一标识符。
    """
    user = User.get_queryset().get(id=user_id)
    return await UserPydantic.from_queryset_single(user)


@user_router.put("/{user_id}", summary="更新用户信息", response_model=UserPydantic,
                 responses={404: {"model": HTTPNotFoundError}})
async def update_user(user_id: int, user: UserUpdatePydantic):
    """
    更新指定 ID 用户的信息。
    - **user_id**: 要更新的用户的唯一标识符。
    - **user**: 更新后的用户详细信息。
    """
    await User.get_queryset().filter(id=user_id).update(**user.dict(exclude_unset=True))
    user = User.get_queryset().get(id=user_id)
    return await UserPydantic.from_queryset_single(user)


@user_router.patch(
    "/{user_id}", summary="部分更新用户信息", response_model=UserPydantic, responses={404: {"model": HTTPNotFoundError}}
)
async def patch_user(user_id: int, user: UserUpdatePydantic):
    """
    部分更新指定 ID 用户的信息。
    - **user_id**: 要更新的用户的唯一标识符。
    - **user**: 更新后的用户详细信息（仅更新提供的字段）。
    """
    await User.get_queryset().filter(id=user_id).update(**user.dict(exclude_unset=True))
    user = User.get_queryset().get(id=user_id)
    return await UserPydantic.from_queryset_single(user)


@user_router.delete("/{user_id}", summary="删除用户", response_model=dict, responses={404: {"model": HTTPNotFoundError}})
async def delete_user(user_id: int):
    """
    删除指定 ID 的用户。
    - **user_id**: 要删除的用户的唯一标识符。
    """
    deleted_count = await User.get_queryset().filter(id=user_id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return {"deleted": deleted_count}


# 获取用户的角色列表
@user_router.get("/{user_id}/roles", summary="获取用户角色列表", response_model=List[RolePydantic],
                 responses={404: {"model": HTTPNotFoundError}})
async def get_user_roles(user_id: int):
    """
    获取指定用户的角色列表。
    - **user_id**: 用户的唯一标识符。
    """
    user = await User.get_queryset().prefetch_related("roles").get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return await RolePydantic.from_queryset(user.roles.all())


# 获取用户的权限列表
@user_router.get("/{user_id}/permissions", summary="获取用户权限列表", response_model=List[PermissionPydantic],
                 responses={404: {"model": HTTPNotFoundError}})
async def get_user_permissions(user_id: int):
    """
    获取指定用户的权限列表。
    - **user_id**: 用户的唯一标识符。
    """
    user = await User.get_queryset().prefetch_related("roles__permissions").get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    # 获取用户所有角色的权限
    permissions = set()
    for role in user.roles:
        for permission in role.permissions:
            permissions.add(permission)

    return await PermissionPydantic.from_queryset(Permission.filter(id__in=[perm.id for perm in permissions]))


# 用户添加角色
@user_router.post("/{user_id}/roles", summary="为用户添加角色", response_model=UserPydantic)
async def add_role_to_user(user_id: int, role_ids: List[int]):
    """
    为用户添加一个或多个角色。
    - **user_id**: 用户的唯一标识符。
    - **role_ids**: 要添加的角色的唯一标识符列表。
    """
    user = await User.get_queryset().get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    roles = await Role.get_queryset().filter(id__in=role_ids).all()
    if len(roles) != len(role_ids):
        missing_ids = set(role_ids) - {role.id for role in roles}
        raise HTTPException(status_code=404, detail=f"Roles with IDs {missing_ids} not found")

    await user.roles.add(*roles)
    return await UserPydantic.from_queryset_single(User.get_queryset().get(id=user_id))


# 用户修改角色
@user_router.put("/{user_id}/roles", summary="修改用户角色", response_model=UserPydantic)
async def update_roles_for_user(user_id: int, role_ids: List[int]):
    """
    修改用户的角色（覆盖更新）。
    - **user_id**: 用户的唯一标识符。
    - **role_ids**: 要设置的角色的唯一标识符列表。
    """
    user = await User.get_queryset().get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    roles = await Role.filter(id__in=role_ids).all()
    if len(roles) != len(role_ids):
        missing_ids = set(role_ids) - {role.id for role in roles}
        raise HTTPException(status_code=404, detail=f"Roles with IDs {missing_ids} not found")

    await user.roles.clear()
    await user.roles.add(*roles)
    return await UserPydantic.from_queryset_single(User.get_queryset().get(id=user_id))


# 用户删除角色
@user_router.delete("/{user_id}/roles", summary="删除用户角色", response_model=UserPydantic)
async def delete_roles_from_user(user_id: int, role_ids: List[int]):
    """
    删除用户的一个或多个角色。
    - **user_id**: 用户的唯一标识符。
    - **role_ids**: 要删除的角色的唯一标识符列表。
    """
    user = await User.get_queryset().get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    roles = await Role.get_queryset().filter(id__in=role_ids).all()
    if len(roles) != len(role_ids):
        missing_ids = set(role_ids) - {role.id for role in roles}
        raise HTTPException(status_code=404, detail=f"Roles with IDs {missing_ids} not found")

    await user.roles.remove(*roles)
    return await UserPydantic.from_queryset_single(User.get_queryset().get(id=user_id))


# 用户添加权限
@user_router.post("/{user_id}/permissions", summary="为用户添加权限", response_model=UserPydantic)
async def add_permission_to_user(user_id: int, permission_ids: List[int]):
    """
    为用户添加一个或多个权限。
    - **user_id**: 用户的唯一标识符。
    - **permission_ids**: 要添加的权限的唯一标识符列表。
    """
    user = await User.get_queryset().get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    permissions = await Permission.get_queryset().filter(id__in=permission_ids).all()
    if len(permissions) != len(permission_ids):
        missing_ids = set(permission_ids) - {permission.id for permission in permissions}
        raise HTTPException(status_code=404, detail=f"Permissions with IDs {missing_ids} not found")

    await user.permissions.add(*permissions)
    return await UserPydantic.from_queryset_single(User.get_queryset().get(id=user_id))


# 用户删除权限
@user_router.delete("/{user_id}/permissions", summary="删除用户权限", response_model=UserPydantic)
async def delete_permission_from_user(user_id: int, permission_ids: List[int]):
    """
    删除用户的一个或多个权限。
    - **user_id**: 用户的唯一标识符。
    - **permission_ids**: 要删除的权限的唯一标识符列表。
    """
    user = await User.get_queryset().get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    permissions = await Permission.get_queryset().filter(id__in=permission_ids).all()
    if len(permissions) != len(permission_ids):
        missing_ids = set(permission_ids) - {permission.id for permission in permissions}
        raise HTTPException(status_code=404, detail=f"Permissions with IDs {missing_ids} not found")

    await user.permissions.remove(*permissions)
    return await UserPydantic.from_queryset_single(User.get_queryset().get(id=user_id))


# 用户修改权限
@user_router.put("/{user_id}/permissions", summary="修改用户权限", response_model=UserPydantic)
async def update_permissions_for_user(user_id: int, permission_ids: List[int]):
    """
    修改用户的权限（覆盖更新）。
    - **user_id**: 用户的唯一标识符。
    - **permission_ids**: 要设置的权限的唯一标识符列表。
    """
    user = await User.get_queryset().get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    permissions = await Permission.get_queryset().filter(id__in=permission_ids).all()
    if len(permissions) != len(permission_ids):
        missing_ids = set(permission_ids) - {permission.id for permission in permissions}
        raise HTTPException(status_code=404, detail=f"Permissions with IDs {missing_ids} not found")

    await user.permissions.clear()
    await user.permissions.add(*permissions)
    return await UserPydantic.from_queryset_single(User.get_queryset().get(id=user_id))
