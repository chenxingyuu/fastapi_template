from typing import List

from fastapi import APIRouter, Depends, HTTPException, Security
from tortoise.contrib.fastapi import HTTPNotFoundError

from app.system.filters import ListUserFilterSet
from app.system.models import Permission, Role, User
from app.system.serializers import (
    PermissionDetail,
    RoleDetail,
    UserCreate,
    UserDetail,
    UserPatch,
    UserUpdate,
)
from app.system.views.auth import get_current_active_user
from cores.paginate import PageModel, PaginationParams, paginate
from cores.pwd import get_password_hash
from cores.response import ResponseModel

user_router = APIRouter()
user_me_router = APIRouter()
user_role_route = APIRouter()
user_permission_route = APIRouter()


async def validate_user(user_id: int) -> User:
    if not (user := await User.get_queryset().get_or_none(id=user_id)):
        raise HTTPException(
            status_code=404, detail=f"User {user_id} not found"
        )
    return user


@user_router.post(
    path="",
    summary="创建用户",
    response_model=ResponseModel[UserDetail],
    dependencies=[
        Security(get_current_active_user, scopes=["system:user:create"])
    ],
)
async def create_user(user: UserCreate):
    """
    创建一个新的系统用户。
    - **user**: 要创建的用户的详细信息。
    """
    password = f"{user.username}@123456"
    hashed_password = get_password_hash(password)
    user_obj = await User.create(
        **user.dict(exclude_unset=True), hashed_password=hashed_password
    )
    user_data = await UserDetail.from_tortoise_orm(user_obj)
    return ResponseModel(data=user_data)


@user_router.get(
    "",
    summary="获取用户列表",
    response_model=ResponseModel[PageModel[UserDetail]],
    dependencies=[
        Security(get_current_active_user, scopes=["system:user:read"])
    ],
)
async def list_user(
    user_filter: ListUserFilterSet = Depends(),
    pagination: PaginationParams = Depends(),
):
    """
    获取系统用户列表，支持多种过滤条件。
    - **username**: 用户名过滤条件（模糊匹配）。
    - **email**: 电子邮件过滤条件（模糊匹配）。
    - **is_active**: 是否激活过滤条件。
    - **is_superuser**: 是否超级用户过滤条件。
    """
    query = user_filter.apply_filters()
    page_data = await paginate(query, pagination, UserDetail)
    return ResponseModel(data=page_data)


@user_me_router.get(
    "/me",
    summary="获取我的详细信息",
    response_model=ResponseModel[UserDetail],
    dependencies=[
        Security(
            get_current_active_user,
            scopes=["system:user:me:read"],
        )
    ],
)
async def get_user_me(current_user: User = Depends(get_current_active_user)):
    user_data = UserDetail.from_orm(current_user)
    return ResponseModel(data=user_data)


@user_me_router.put(
    "/me",
    summary="更新我的详细信息",
    response_model=ResponseModel[UserDetail],
    dependencies=[
        Security(
            get_current_active_user,
            scopes=["system:user:me:update"],
        )
    ],
)
async def update_user_me(
    user: UserUpdate, current_user: User = Depends(get_current_active_user)
):
    updated_count = (
        await User.get_queryset()
        .filter(id=current_user.id)
        .update(**user.dict(exclude_unset=True))
    )
    if not updated_count:
        raise HTTPException(
            status_code=404, detail=f"User {current_user.id} not found"
        )
    user_obj = await User.get_queryset().get(id=current_user.id)
    user_data = await UserDetail.from_tortoise_orm(user_obj)
    return ResponseModel(data=user_data)


@user_me_router.delete(
    "/me",
    summary="删除自己的账号",
    response_model=ResponseModel[dict],
    responses={404: {"model": HTTPNotFoundError}},
    dependencies=[
        Security(get_current_active_user, scopes=["system:user:me:delete"])
    ],
)
async def delete_user_me(
    current_user: User = Depends(get_current_active_user),
):
    """
    删除指定 ID 的用户。
    - **user_id**: 要删除的用户的唯一标识符。
    """
    deleted_count = (
        await User.get_queryset().filter(id=current_user.id).delete()
    )
    if not deleted_count:
        raise HTTPException(
            status_code=404, detail=f"User {current_user.id} not found"
        )
    return ResponseModel(data={"deleted": deleted_count})


@user_me_router.get(
    "/me/roles",
    summary="获取我的角色",
    response_model=ResponseModel[List[RoleDetail]],
    dependencies=[
        Security(
            get_current_active_user,
            scopes=["system:user:me:read", "system:role:me:read"],
        )
    ],
)
async def get_user_me_roles(
    current_user: User = Depends(get_current_active_user),
):
    roles_data = await RoleDetail.from_queryset(current_user.roles.all())
    return ResponseModel(data=roles_data)


@user_me_router.get(
    "/me/permissions",
    summary="获取我的权限",
    response_model=ResponseModel[List[PermissionDetail]],
    dependencies=[
        Security(
            get_current_active_user,
            scopes=["system:user:me:read", "system:permission:me:read"],
        )
    ],
)
async def get_user_me_permissions(
    current_user: User = Depends(get_current_active_user),
):
    permissions_data = await PermissionDetail.from_queryset(
        current_user.permissions.all()
    )
    return ResponseModel(data=permissions_data)


@user_router.get(
    "/{user_id}",
    summary="获取用户详细信息",
    response_model=ResponseModel[UserDetail],
    responses={404: {"model": HTTPNotFoundError}},
    dependencies=[
        Security(get_current_active_user, scopes=["system:user:read"])
    ],
)
async def get_user(user_id: int):
    """
    根据用户 ID 获取单个用户的详细信息。
    - **user_id**: 用户的唯一标识符。
    """
    user = await User.get_queryset().get_or_none(id=user_id)
    if not user:
        raise HTTPException(
            status_code=404, detail=f"User {user_id} not found"
        )
    user_data = await UserDetail.from_tortoise_orm(user)
    return ResponseModel(data=user_data)


@user_router.put(
    "/{user_id}",
    summary="更新用户信息",
    response_model=ResponseModel[UserDetail],
    responses={404: {"model": HTTPNotFoundError}},
    dependencies=[
        Security(get_current_active_user, scopes=["system:user:update"])
    ],
)
async def update_user(user_id: int, user: UserUpdate):
    """
    更新指定 ID 用户的信息。
    - **user_id**: 要更新的用户的唯一标识符。
    - **user**: 更新后的用户详细信息。
    """
    user_obj = await User.get_queryset().get(id=user_id)
    if not user_obj:
        raise HTTPException(
            status_code=404, detail=f"User {user_id} not found"
        )
    await User.get_queryset().filter(id=user_id).update(**user.dict(exclude_unset=True))

    user_data = await UserDetail.from_tortoise_orm(user_obj)
    return ResponseModel(data=user_data)


@user_router.patch(
    "/{user_id}",
    summary="部分更新用户信息",
    response_model=ResponseModel[UserDetail],
    responses={404: {"model": HTTPNotFoundError}},
    dependencies=[
        Security(get_current_active_user, scopes=["system:user:update"])
    ],
)
async def patch_user(user_id: int, user: UserPatch):
    """
    部分更新指定 ID 用户的信息。
    - **user_id**: 要更新的用户的唯一标识符。
    - **user**: 更新后的用户详细信息（仅更新提供的字段）。
    """
    updated_count = (
        await User.get_queryset()
        .filter(id=user_id)
        .update(**user.dict(exclude_unset=True))
    )
    if not updated_count:
        raise HTTPException(
            status_code=404, detail=f"User {user_id} not found"
        )
    user_obj = await User.get_queryset().get(id=user_id)
    user_data = await UserDetail.from_tortoise_orm(user_obj)
    return ResponseModel(data=user_data)


@user_router.delete(
    "/{user_id}",
    summary="删除用户",
    response_model=ResponseModel[dict],
    responses={404: {"model": HTTPNotFoundError}},
    dependencies=[
        Security(get_current_active_user, scopes=["system:user:delete"])
    ],
)
async def delete_user(user_id: int):
    """
    删除指定 ID 的用户。
    - **user_id**: 要删除的用户的唯一标识符。
    """
    deleted_count = await User.get_queryset().filter(id=user_id).delete()
    if not deleted_count:
        raise HTTPException(
            status_code=404, detail=f"User {user_id} not found"
        )
    return ResponseModel(data={"deleted": deleted_count})


# 获取用户的角色列表
@user_role_route.get(
    "/{user_id}/roles",
    summary="获取用户角色列表",
    response_model=ResponseModel[List[RoleDetail]],
    responses={404: {"model": HTTPNotFoundError}},
    dependencies=[
        Security(
            get_current_active_user,
            scopes=["system:user:read", "system:role:read"],
        )
    ],
)
async def get_user_roles(user_id: int):
    """
    获取指定用户的角色列表。
    - **user_id**: 用户的唯一标识符。
    """
    user = (
        await User.get_queryset()
        .prefetch_related("roles")
        .get_or_none(id=user_id)
    )
    if not user:
        raise HTTPException(
            status_code=404, detail=f"User {user_id} not found"
        )
    roles_data = await RoleDetail.from_queryset(user.roles.all())
    return ResponseModel(data=roles_data)


# 获取用户的权限列表
@user_permission_route.get(
    "/{user_id}/permissions",
    summary="获取用户权限列表",
    response_model=ResponseModel[List[PermissionDetail]],
    responses={404: {"model": HTTPNotFoundError}},
    dependencies=[
        Security(
            get_current_active_user,
            scopes=["system:user:read", "system:permission:read"],
        )
    ],
)
async def get_user_permissions(user_id: int):
    """
    获取指定用户的权限列表。
    - **user_id**: 用户的唯一标识符。
    """
    user = await validate_user(user_id)

    permissions_data = await PermissionDetail.from_queryset(
        user.permissions.all()
    )
    return ResponseModel(data=permissions_data)


# 用户添加角色
@user_role_route.post(
    "/{user_id}/roles",
    summary="为用户添加角色",
    response_model=ResponseModel[List[RoleDetail]],
    dependencies=[
        Security(
            get_current_active_user,
            scopes=["system:user:update", "system:role:read"],
        )
    ],
)
async def add_role_to_user(user_id: int, role_ids: List[int]):
    """
    为用户添加一个或多个角色。
    - **user_id**: 用户的唯一标识符。
    - **role_ids**: 要添加的角色的唯一标识符列表。
    """
    user = await validate_user(user_id)

    roles = await Role.get_queryset().filter(id__in=role_ids).all()
    if len(roles) != len(role_ids):
        missing_ids = set(role_ids) - {role.id for role in roles}
        raise HTTPException(
            status_code=404,
            detail=f"Roles with IDs {missing_ids} not found",
        )

    await user.roles.add(*roles)

    # 获取更新后的用户数据
    updated_user = await User.get_queryset().get(id=user_id)
    role_data = await RoleDetail.from_queryset(updated_user.roles.all())
    return ResponseModel(data=role_data)


# 用户修改角色
@user_role_route.put(
    "/{user_id}/roles",
    summary="修改用户角色",
    response_model=ResponseModel[List[RoleDetail]],
    dependencies=[
        Security(
            get_current_active_user,
            scopes=["system:user:update", "system:role:read"],
        )
    ],
)
async def update_roles_for_user(user_id: int, role_ids: List[int]):
    """
    修改用户的角色（覆盖更新）。
    - **user_id**: 用户的唯一标识符。
    - **role_ids**: 要设置的角色的唯一标识符列表。
    """
    user = await validate_user(user_id)

    roles = await Role.get_queryset().filter(id__in=role_ids).all()
    if len(roles) != len(role_ids):
        missing_ids = set(role_ids) - {role.id for role in roles}
        raise HTTPException(
            status_code=404,
            detail=f"Roles with IDs {missing_ids} not found",
        )

    await user.roles.clear()
    await user.roles.add(*roles)

    # 获取更新后的用户数据
    updated_user = await User.get_queryset().get(id=user_id)
    role_data = await RoleDetail.from_queryset(updated_user.roles.all())
    return ResponseModel(data=role_data)


# 用户删除角色
@user_role_route.delete(
    "/{user_id}/roles",
    summary="删除用户角色",
    response_model=ResponseModel[List[RoleDetail]],
    dependencies=[
        Security(
            get_current_active_user,
            scopes=["system:user:update", "system:role:read"],
        )
    ],
)
async def delete_roles_from_user(user_id: int, role_ids: List[int]):
    """
    删除用户的一个或多个角色。
    - **user_id**: 用户的唯一标识符。
    - **role_ids**: 要删除的角色的唯一标识符列表。
    """
    user = await validate_user(user_id)

    roles = await Role.get_queryset().filter(id__in=role_ids).all()
    if len(roles) != len(role_ids):
        missing_ids = set(role_ids) - {role.id for role in roles}
        raise HTTPException(
            status_code=404,
            detail=f"Roles with IDs {missing_ids} not found",
        )

    await user.roles.remove(*roles)

    # 获取更新后的用户数据
    updated_user = await User.get_queryset().get(id=user_id)
    role_data = await RoleDetail.from_queryset(updated_user.roles.all())
    return ResponseModel(data=role_data)


# 用户添加权限
@user_permission_route.post(
    "/{user_id}/permissions",
    summary="为用户添加权限",
    response_model=ResponseModel[List[PermissionDetail]],
    dependencies=[
        Security(
            get_current_active_user,
            scopes=["system:user:update", "system:permission:read"],
        )
    ],
)
async def add_permission_to_user(user_id: int, permission_ids: List[int]):
    """
    为用户添加一个或多个权限。
    - **user_id**: 用户的唯一标识符。
    - **permission_ids**: 要添加的权限的唯一标识符列表。
    """
    user = await validate_user(user_id)

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

    await user.permissions.add(*permissions)

    # 获取更新后的用户数据
    updated_user = await User.get_queryset().get(id=user_id)
    permission_data = await PermissionDetail.from_queryset(
        updated_user.permissions.all()
    )
    return ResponseModel(data=permission_data)


# 用户删除权限
@user_permission_route.delete(
    "/{user_id}/permissions",
    summary="删除用户权限",
    response_model=ResponseModel[List[PermissionDetail]],
    dependencies=[
        Security(
            get_current_active_user,
            scopes=["system:user:update", "system:permission:read"],
        )
    ],
)
async def delete_permission_from_user(user_id: int, permission_ids: List[int]):
    """
    删除用户的一个或多个权限。
    - **user_id**: 用户的唯一标识符。
    - **permission_ids**: 要删除的权限的唯一标识符列表。
    """
    user = await validate_user(user_id)

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

    await user.permissions.remove(*permissions)

    # 获取更新后的用户数据
    updated_user = await User.get_queryset().get(id=user_id)
    permission_data = await PermissionDetail.from_queryset(
        updated_user.permissions.all()
    )
    return ResponseModel(data=permission_data)


# 用户修改权限
@user_permission_route.put(
    "/{user_id}/permissions",
    summary="修改用户权限",
    response_model=ResponseModel[List[PermissionDetail]],
    dependencies=[
        Security(
            get_current_active_user,
            scopes=["system:user:update", "system:permission:read"],
        )
    ],
)
async def update_permissions_for_user(user_id: int, permission_ids: List[int]):
    """
    修改用户的权限（覆盖更新）。
    - **user_id**: 用户的唯一标识符。
    - **permission_ids**: 要设置的权限的唯一标识符列表。
    """
    user = await validate_user(user_id)

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

    await user.permissions.clear()
    await user.permissions.add(*permissions)

    # 获取更新后的用户数据
    updated_user = await User.get_queryset().get(id=user_id)
    permission_data = await PermissionDetail.from_queryset(
        updated_user.permissions.all()
    )
    return ResponseModel(data=permission_data)
