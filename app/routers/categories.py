from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update

from sqlalchemy.ext.asyncio import AsyncSession
from app.db_depends import get_async_db

from app.models.categories import Category as CategoryModel
from app.schemas import Category as CategorySchema, CategoryCreate
from app.models.users import User as UserModel

from app.auth import get_current_admin

# создание роутера маршрута для категорий
router = APIRouter(
    prefix="/categories",
    tags=["categories"]
)

@router.get("/",
            response_model=list[CategorySchema],
            status_code=status.HTTP_200_OK)
async def read_categories(db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает список всех активных категорий.
    :param db:
    :return:
    """
    stmt = select(CategoryModel).where(CategoryModel.is_active == True)
    result = await db.scalars(stmt)
    categories = result.all()
    return categories


@router.get("/{category_id}",
            response_model=CategorySchema,
            status_code=status.HTTP_200_OK)
async def read_category(category_id: int,
                        db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает категорию по id
    :param category_id:
    :return:
    """
    # Проверка существования категории
    stmt = select(CategoryModel).where(CategoryModel.id == category_id).where(CategoryModel.is_active == True)
    result = await db.scalars(stmt)
    category = result.first()
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    return category


@router.post("/",
             response_model=CategorySchema,
             status_code=status.HTTP_201_CREATED)
async def create_category(category: CategoryCreate,
                          db: AsyncSession = Depends(get_async_db),
                          current_user: UserModel = Depends(get_current_admin)):
    """
    Создание новой категории
    :param category:
    :param db:
    :return:
    """
    # проверка существования parent_id, если указан
    if category.parent_id is not None:
        stmt = select(CategoryModel).where(CategoryModel.id == category.parent_id).where(CategoryModel.is_active == True)
        result = await db.scalars(stmt)
        parent = result.first()
        if parent is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Parent category not found")

    # создание новой категории
    db_category = CategoryModel(**category.model_dump())
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category


@router.put("/{category_id}",
            response_model=CategorySchema)
async def update_category(category_id: int,
                          category: CategoryCreate,
                          db: AsyncSession = Depends(get_async_db),
                          current_user: UserModel = Depends(get_current_admin)):
    """
    Целиком заменяет категорию по ID
    :param category_id:
    :return:
    """
    # Проверка существования категории
    stmt = select(CategoryModel).where(CategoryModel.id == category_id).where(CategoryModel.is_active == True)
    result = await db.scalars(stmt)
    db_category = result.first()
    if db_category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    # Проверка существования parent_id, если указан
    if category.parent_id is not None:
        parent_stmt = select(CategoryModel).where(CategoryModel.parent_id == category.parent_id).where(CategoryModel.is_active == True)
        result = await db.scalars(parent_stmt)
        parent = result.first()
        if parent is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Parent category not found")

    # Обновление категории
    await db.execute(
        update(CategoryModel)
        .where(CategoryModel.id == category_id)
        .values(**category.model_dump())
    )
    await db.commit()
    await db.refresh(db_category)
    return db_category


@router.delete("/{category_id}",
               status_code=status.HTTP_200_OK)
async def delete_category(category_id: int,
                          db: AsyncSession = Depends(get_async_db),
                          current_user: UserModel = Depends(get_current_admin)):
    """
    Логически удаляет категорию по её ID, устанавливая is_active=False
    :param category_id:
    :param db:
    :return:
    """
    # Проверка существования активной категории
    stmt = select(CategoryModel).where(CategoryModel.id == category_id).where(CategoryModel.is_active == True)
    result = await db.scalars(stmt)
    category = result.first()
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    # логическое удаление категории (установка is_active = False)
    await db.execute(update(CategoryModel).where(CategoryModel.id == category_id).values(is_active=False))
    await db.commit()
    await db.refresh(category)

    return {"status": "success", "message": "Category marked as inactive"}