from typing import List, Optional

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


class MenuDetailTree(MenuDetail):
    children: Optional[List["MenuDetailTree"]] = []

    @classmethod
    def from_menu_list(cls, menus: List[MenuDetail]) -> List["MenuDetailTree"]:
        menu_dict = {menu.id: cls.from_orm(menu) for menu in menus}
        tree = []

        for menu in menus:
            menu_tree = menu_dict[menu.id]
            if menu_tree.parent_id is None:
                tree.append(menu_tree)
            else:
                parent = menu_dict.get(menu_tree.parent_id)
                if parent:
                    parent.children.append(menu_tree)
        return tree


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
