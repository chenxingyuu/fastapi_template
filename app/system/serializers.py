# Pydantic 模型
from typing import List

from tortoise.contrib.pydantic import pydantic_model_creator

from app.system.models import Permission, Role, User

PermissionPydantic = pydantic_model_creator(Permission, exclude=("created_at", "updated_at", "deleted_at"))
RolePydantic = pydantic_model_creator(Role, exclude=("created_at", "updated_at", "deleted_at"))
UserPydantic = pydantic_model_creator(User, exclude=("hashed_password",))

PermissionCreatePydantic = pydantic_model_creator(
    Permission, name="PermissionIn", exclude=("id", "created_at", "updated_at", "deleted_at")
)
PermissionUpdatePydantic = pydantic_model_creator(Permission, name="PermissionUpdate", exclude_readonly=True)

UserCreatePydantic = pydantic_model_creator(
    User,
    name="UserIn",
    exclude=("id", "hashed_password", "created_at", "updated_at", "deleted_at", "is_active", "is_superuser", "roles"),
)
UserUpdatePydantic = pydantic_model_creator(User, name="UserUpdate", exclude_readonly=True)


class RoleWithPermissionsPydantic(RolePydantic):
    permissions: List[PermissionPydantic]


class UserWithRolePydantic(RolePydantic):
    roles: List[RolePydantic]


class UserWithRolePermissionsPydantic(RolePydantic):
    roles: List[RolePydantic]
    permissions: List[PermissionPydantic]


RoleCreatePydantic = pydantic_model_creator(Role, name="Role", exclude=("id", "created_at", "updated_at", "deleted_at"))
RoleUpdatePydantic = pydantic_model_creator(Role, name="RoleUpdate", exclude_readonly=True)
