from fastapi import APIRouter

# создание роутера маршрута для категорий
router = APIRouter(
    prefix="/categories",
    tags=["categories"]
)

@router.get("/")
async def read_categories():
    """
    Возвращает список всех категорий
    :return:
    """
    pass


@router.get("/{category_id}")
async def read_category(category_id: int):
    """
    Возвращает категорию по id
    :param category_id:
    :return:
    """
    pass


@router.post("/")
async def create_category():
    """
    Создание всех категорий
    :return:
    """
    pass

@router.put("/{category_id}")
async def update_category(category_id: int):
    """
    Целиком заменяет категорию по ID
    :param category_id:
    :return:
    """
    pass

@router.delete("/{category_id}")
async def delete_category(category_id: int):
    """
    Вносит частичное изменение в категорию по ID
    :param category_id:
    :return:
    """
    pass