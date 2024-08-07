# Pydantic 模型
from typing import List, Optional

from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator

from app.system.models import Permission, Role, User

PermissionPydantic = pydantic_model_creator(Permission, name="PermissionPydantic")
UserPydantic = pydantic_model_creator(User, name="UserPydantic")
CreatorPydantic = pydantic_model_creator(User, name="CreatorPydantic", include=("id", "username"))
RolePydantic = pydantic_model_creator(Role, name="RolePydantic")


# ===============================================================================================
# Permission
# ===============================================================================================


class PermissionDetail(PermissionPydantic):
    creator: Optional[CreatorPydantic]
    roles: List[RolePydantic]
    users: List[UserPydantic]


PermissionCreate = pydantic_model_creator(Permission, name="PermissionCreate", include=("name", "description"))
PermissionUpdate = PermissionCreate
PermissionPatch = PermissionCreate

# ===============================================================================================
# Role
# ===============================================================================================
RoleDetail = pydantic_model_creator(Role, name="RoleDetail")
RoleCreate = pydantic_model_creator(Role, name="RoleCreate", include=("name", "description"))
RoleUpdate = RoleCreate
RolePatch = RoleCreate

# ===============================================================================================
# User
# ===============================================================================================
UserDetail = pydantic_model_creator(User, name="UserDetail", exclude=("hashed_password", "creator"))


class UserWithRoleDetail(UserDetail):
    roles: List[RoleDetail]


class UserWithPermissionDetail(UserDetail):
    permissions: List[PermissionDetail]


class UserPassword(User):
    password = fields.CharField(max_length=255)


UserCreate = pydantic_model_creator(UserPassword, name="UserCreate", include=("username", "password"))
UserUpdate = pydantic_model_creator(User, name="UserUpdate", exclude=("id", "created_at", "updated_at", "deleted_at"))
UserPatch = pydantic_model_creator(User, name="UserPatch", exclude=("id", "created_at", "updated_at", "deleted_at"))
