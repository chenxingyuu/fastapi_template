import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Security
from tortoise.contrib.fastapi import HTTPNotFoundError
from tortoise.exceptions import DoesNotExist

from app.system.filters import ListMenuFilterSet
from app.system.models import Menu, User
from app.system.serializers.menus import MenuDetail, MenuCreate, MenuUpdate, MenuPatch
from app.system.views.auth import get_current_active_user
from cores.paginate import PageModel, PaginationParams, paginate
from cores.response import ResponseModel

menu_router = APIRouter()


@menu_router.post(
    "",
    summary="创建权限",
    response_model=ResponseModel[MenuDetail],
    dependencies=[Security(get_current_active_user, scopes=["system:menu:create"])],
)
async def create_menu(
    menu: MenuCreate,
    current_user: User = Depends(get_current_active_user),
):
    """
    创建一个新的权限。
    - **Menu**: 要创建的权限的详细信息。
    """
    menu_obj = await Menu.create(**menu.dict(), creator_id=current_user.id)
    response = await MenuDetail.from_tortoise_orm(menu_obj)
    return ResponseModel(data=response)


@menu_router.get(
    "",
    summary="获取权限列表",
    response_model=ResponseModel[PageModel[MenuDetail]],
    dependencies=[Security(get_current_active_user, scopes=["system:menu:read"])],
)
async def list_menus(
    menu_filter: ListMenuFilterSet = Depends(),
    pagination: PaginationParams = Depends(),
):
    """
    获取所有权限的列表，可以按名称和描述进行搜索。
    """
    query = menu_filter.apply_filters()
    page_data = await paginate(query, pagination, MenuDetail)
    return ResponseModel(data=page_data)


@menu_router.get(
    "/all",
    summary="获取所有权限列表",
    response_model=ResponseModel[List[MenuDetail]],
    dependencies=[Security(get_current_active_user, scopes=["system:Menu:read"])],
)
async def all_menus(
    menu_filter: ListMenuFilterSet = Depends(),
):
    """
    获取所有权限的列表，可以按名称和描述进行搜索。
    """
    query = menu_filter.apply_filters()
    Menus = await MenuDetail.from_queryset(query)
    return ResponseModel(data=Menus)


@menu_router.get(
    "/{menu_id}",
    summary="获取权限详细信息",
    response_model=ResponseModel[MenuDetail],
    responses={404: {"model": HTTPNotFoundError}},
    dependencies=[Security(get_current_active_user, scopes=["system:menu:read"])],
)
async def get_menu(menu_id: int):
    """
    根据权限 ID 获取单个权限的详细信息。
    - **menu_id**: 权限的唯一标识符。
    """
    try:
        menu = Menu.get_queryset().get(id=menu_id)
        response = await MenuDetail.from_queryset_single(menu)
        return ResponseModel(data=response)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Menu {menu_id} not found")


@menu_router.put(
    "/{menu_id}",
    summary="更新权限信息",
    response_model=ResponseModel[MenuDetail],
    responses={404: {"model": HTTPNotFoundError}},
    dependencies=[Security(get_current_active_user, scopes=["system:menu:update"])],
)
async def update_menu(menu_id: int, menu: MenuUpdate):
    """
    更新指定 ID 权限的信息。
    - **menu_id**: 要更新的权限的唯一标识符。
    - **menu**: 更新后的权限详细信息。
    """
    menu_obj = await Menu.get_queryset().get_or_none(id=menu_id)
    if not menu_obj:
        raise HTTPException(status_code=404, detail=f"Menu {menu_id} not found")

    await Menu.get_queryset().filter(id=menu_id).update(**menu.dict(exclude_unset=True))
    updated_menu = Menu.get_queryset().get(id=menu_id)
    response = await MenuDetail.from_queryset_single(updated_menu)
    return ResponseModel(data=response)


@menu_router.patch(
    "/{menu_id}",
    summary="部分更新权限信息",
    response_model=ResponseModel[MenuDetail],
    responses={404: {"model": HTTPNotFoundError}},
    dependencies=[Security(get_current_active_user, scopes=["system:menu:update"])],
)
async def patch_menu(menu_id: int, menu: MenuPatch):
    """
    部分更新指定 ID 权限的信息。
    - **menu_id**: 要更新的权限的唯一标识符。
    - **menu**: 更新后的权限详细信息（仅更新提供的字段）。
    """
    menu_obj = await Menu.get_queryset().get_or_none(id=menu_id)
    if not menu_obj:
        raise HTTPException(status_code=404, detail=f"Menu {menu_id} not found")

    await Menu.get_queryset().filter(id=menu_id).update(**menu.dict(exclude_unset=True))
    updated_menu = Menu.get_queryset().get(id=menu_id)
    response = await MenuDetail.from_queryset_single(updated_menu)
    return ResponseModel(data=response)


@menu_router.delete(
    "/{menu_id}",
    summary="删除权限",
    response_model=ResponseModel[dict],
    responses={404: {"model": HTTPNotFoundError}},
    dependencies=[Security(get_current_active_user, scopes=["system:menu:delete"])],
)
async def delete_menu(menu_id: int):
    """
    逻辑删除指定 ID 的权限。
    - **menu_id**: 要删除的权限的唯一标识符。
    """
    try:
        menu = await Menu.get_queryset().get(id=menu_id)
        Menu.deleted_at = datetime.datetime.now()
        await menu.save()
        return ResponseModel(data={"deleted": 1})
    except DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Menu {menu_id} not found")
