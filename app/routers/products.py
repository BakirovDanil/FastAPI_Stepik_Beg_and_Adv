from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import User as UserModel
from app.models.categories import Category as CategoryModel
from app.models.products import Product as ProductModel
from app.schemas import Product as ProductSchema, ProductCreate

from app.db_depends import get_async_db

from app.auth import get_current_seller


# создание роутера маршрута для товаров
router = APIRouter(
    prefix="/products",
    tags=["products"]
)

@router.get("/",
            response_model=list[ProductSchema],
            status_code=status.HTTP_200_OK)
async def read_products(db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает все продукты. Если таковых нет, возвращает пустой список
    :param db:
    :return:
    """
    stmt = (select(ProductModel)
            .join(CategoryModel)
            .where(ProductModel.is_active == True)
            .where(CategoryModel.is_active == True)
            )
    products = (await db.scalars(stmt)).all()
    return products


@router.get("/{product_id}",
            response_model=ProductSchema)
async def read_product(product_id: int,
                       db: AsyncSession = Depends(get_async_db)):
    """
    Вернуть товар по ID
    :param product_id:
    :return:
    """
    stmt = select(ProductModel).where(ProductModel.id == product_id).where(ProductModel.is_active == True)
    result = await db.scalars(stmt)
    product = result.first()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found or inactive")

    stmt = select(CategoryModel).where(CategoryModel.id == product.category_id).where(CategoryModel.is_active == True)
    result = await db.scalars(stmt)
    category = result.first()
    if category is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category not found or inactive")

    return product


@router.get("/category/{category_id}",
            response_model=list[ProductSchema])
async def read_products_by_category(category_id: int,
                                    db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает список товаров в указанной категории по её ID
    :param category_id:
    :return:
    """
    stmt = select(CategoryModel).where(CategoryModel.id == category_id).where(CategoryModel.is_active == True)
    result = await db.scalars(stmt)
    category = result.first()
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found or inactive")

    stmt = select(ProductModel).where(ProductModel.category_id == category_id).where(ProductModel.is_active == True)
    products = (await db.scalars(stmt)).all()

    return products


@router.post("/",
             response_model=ProductSchema,
             status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate,
                         db: AsyncSession = Depends(get_async_db),
                         current_user: UserModel = Depends(get_current_seller)):
    """
    Создание нового продукта, привязанного  текущему продавцу (только для 'seller')
    :param product:
    :param db:
    :return:
    """
    stmt = select(CategoryModel).where(CategoryModel.id == product.category_id).where(CategoryModel.is_active == True)
    result = await db.scalars(stmt)
    category = result.first()
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found or inactive")

    # Создание нового продукта
    product = ProductModel(**product.model_dump(), seller_id = current_user.id)
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


@router.put("/{product_id}",
            response_model=ProductSchema)
async def update_product(product_id: int,
                         product: ProductCreate,
                         db: AsyncSession = Depends(get_async_db),
                         current_user: UserModel = Depends(get_current_seller)):
    """
    Целиком заменяет товар по ID, если он принадлежит текущему продавцу (только для 'seller').
    :param product_id:
    :return:
    """
    stmt = select(ProductModel).where(ProductModel.id == product_id).where(ProductModel.is_active == True)
    result = await db.scalars(stmt)
    db_product = result.first()
    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found or inactive")
    if db_product.seller_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only update your own products")

    stmt = select(CategoryModel).where(CategoryModel.id == product.category_id).where(CategoryModel.is_active == True)
    result = await db.scalars(stmt)
    category = result.first()
    if category is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category not found or inactive")

    await db.execute(
        update(ProductModel)
        .where(ProductModel.id == product_id)
        .values(**product.model_dump())
    )
    await db.commit()
    await db.refresh(db_product)

    return db_product


@router.delete("/{product_id}", response_model=ProductSchema)
async def delete_product(product_id: int,
                         db: AsyncSession = Depends(get_async_db),
                         current_user: UserModel = Depends(get_current_seller)):
    """
    Логически удаляет продукт по ID, устанавливая is_active = False
    :param product_id:
    :param db:
    :return:
    """
    stmt = select(ProductModel).where(ProductModel.id == product_id).where(ProductModel.is_active == True)
    result = await db.scalars(stmt)
    product = result.first()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found or inactive")
    if product.seller_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own products")

    await db.execute(update(ProductModel).where(ProductModel.id == product_id).values(is_active=False))
    await db.commit()
    await db.refresh(product)

    return product