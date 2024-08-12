# Pydantic 模型
from typing import List

from tortoise.contrib.pydantic import pydantic_model_creator

from app.system.models import Permission, Role, User

PermissionPydantic = pydantic_model_creator(
    Permission, name="PermissionPydantic"
)
UserPydantic = pydantic_model_creator(
    User,
    name="UserPydantic",
    include=("id", "username", "is_active", "is_superuser"),
)
CreatorPydantic = pydantic_model_creator(
    User, name="CreatorPydantic", include=("id", "username")
)
RolePydantic = pydantic_model_creator(Role, name="RolePydantic")

# ===============================================================================================
# Permission
# ===============================================================================================
PermissionDetail = pydantic_model_creator(
    Permission,
    name="PermissionDetail",
    include=(
        "id",
        "name",
        "description",
        "created_at",
        "updated_at",
        "deleted_at",
        "creator_id",
    ),
)
PermissionCreate = pydantic_model_creator(
    Permission, name="PermissionCreate", include=("name", "description")
)
PermissionUpdate = PermissionCreate
PermissionPatch = PermissionCreate

# ===============================================================================================
# Role
# ===============================================================================================
RoleDetail = pydantic_model_creator(
    Role,
    name="RoleDetail",
    include=(
        "id",
        "name",
        "description",
        "created_at",
        "updated_at",
        "deleted_at",
        "creator_id",
    ),
)
RoleCreate = pydantic_model_creator(
    Role, name="RoleCreate", include=("name", "description")
)
RoleUpdate = RoleCreate
RolePatch = RoleCreate

# ===============================================================================================
# User
# ===============================================================================================
UserDetail = pydantic_model_creator(
    User,
    name="UserDetail",
    include=(
        "id",
        "username",
        "is_active",
        "is_superuser",
        "created_at",
        "updated_at",
        "deleted_at",
        "creator_id",
    ),
)


# class UserDetail(UserPydantic):
#     pass


class UserWithRoleDetail(UserDetail):
    roles: List[RoleDetail]


class UserWithPermissionDetail(UserDetail):
    permissions: List[PermissionDetail]


UserCreate = pydantic_model_creator(
    User, name="UserCreate", include=("username",)
)

UserUpdate = pydantic_model_creator(
    User,
    name="UserUpdate",
    include=("username", "is_active"),
)
UserPatch = pydantic_model_creator(
    User,
    name="UserPatch",
    exclude=("id", "created_at", "updated_at", "deleted_at"),
)
