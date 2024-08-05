from tortoise import Tortoise, fields, models
from tortoise.queryset import QuerySet

from cores.config import settings


class SoftDeleteQuerySet(QuerySet):
    def active(self):
        return self.filter(deleted_at=None)


class Model(models.Model):
    id = fields.IntField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    deleted_at = fields.DatetimeField(default=None, null=True)

    class Meta:
        abstract = True

    @classmethod
    def get_queryset(cls):
        return SoftDeleteQuerySet(cls).active()


TORTOISE_ORM = {
    "connections": {"default": settings.mysql.db_url},
    "apps": {
        "models": {
            "models": [
                "app.system.models",
                # "app.blog.models",
                "aerich.models",
            ],
            "default_connection": "default",
        },
    },
}


async def init_db():
    await Tortoise.init(config=TORTOISE_ORM)


async def close_db():
    await Tortoise.close_connections()
