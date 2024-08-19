from tortoise.contrib.pydantic import pydantic_model_creator

from app.system.models import Menu

MenuDetail = pydantic_model_creator(
    Menu,
    name="MenuDetail",
    include=(
        "id",
        "name",
        "path",
        "component_path",
        "locale",
        "icon",
        "requires_auth",
        "parent_id",
    ),
)

MenuCreate = pydantic_model_creator(
    Menu,
    name="MenuCreate",
    include=(
        "name",
        "path",
        "component_path",
        "locale",
        "icon",
        "requires_auth",
        "parent_id",
    ),
)

MenuUpdate = MenuCreate
MenuPatch = MenuCreate
