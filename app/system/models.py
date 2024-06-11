from tortoise import fields

from cores.model import BaseModel


class User(BaseModel):
    username = fields.CharField(max_length=50, unique=True)
    email = fields.CharField(max_length=255, unique=True)
    mobile = fields.CharField(max_length=11, unique=True)
    hashed_password = fields.CharField(max_length=255)
    is_active = fields.BooleanField(default=True)
    is_superuser = fields.BooleanField(default=False)
    roles = fields.ManyToManyField("models.Role", related_name="users", through="sys_user_roles")
    permissions = fields.ManyToManyField("models.Permission", related_name="users", through="sys_user_permissions")

    class Meta:
        table = "system_users"


class Role(BaseModel):
    name = fields.CharField(max_length=50, unique=True)
    description = fields.TextField(null=True)
    permissions = fields.ManyToManyField("models.Permission", related_name="roles", through="sys_role_permissions")

    class Meta:
        table = "system_roles"


class Permission(BaseModel):
    name = fields.CharField(max_length=100, unique=True)
    description = fields.TextField(null=True)

    class Meta:
        table = "system_permissions"
