from fastapi import APIRouter

# создание роутера маршрута для товаров
router = APIRouter(
    prefix="/products",
    tags=["products"]
)

@router.get("/")
async def read_products():
    """
    Возвращает список всех товаров
    :return:
    """
    pass


@router.get("/{product_id}")
async def read_product(product_id: int):
    """
    Вернуть товар по ID
    :param product_id:
    :return:
    """
    pass


@router.get("/category/{category_id}")
async def read_products_by_category(category_id: int):
    """
    Возвращает список товаров в указанной категории по её ID
    :param category_id:
    :return:
    """
    pass


@router.post("/")
async def create_product():
    """
    Создание нового товара
    :return:
    """
    pass


@router.put("/{product_id}")
async def update_product(product_id: int):
    """
    Целиком заменяет товар по ID
    :param product_id:
    :return:
    """
    pass