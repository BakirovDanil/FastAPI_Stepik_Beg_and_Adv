from fastapi import APIRouter, HTTPException, status, Depends

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.sql import func

from app.db_depends import get_async_db

from app.auth import get_current_buyer, get_current_admin

from app.models.reviews import Review as ReviewModel
from app.models.products import Product as ProductModel
from app.models.users import User as UserModel

from app.schemas import ReviewCreate, Review as ReviewSchema


router = APIRouter(prefix="/reviews",
                   tags=["reviews"])


async def update_product_rating(db: AsyncSession,
                                 product_id: int):
    result = await db.execute(
        select(func.avg(ReviewModel.grade)).where(
            ReviewModel.product_id == product_id,
            ReviewModel.is_active == True
        )
    )
    avg_rating = result.scalars().first() or 0.0
    product = await db.get(ProductModel, product_id)
    product.rating = avg_rating
    await db.commit()


@router.get("/",
            response_model=list[ReviewSchema])
async def read_reviews(db: AsyncSession = Depends(get_async_db)):
    """
    Получение списка всех отзывов.
    :param db:
    :return:
    """
    stmt = select(ReviewModel).where(ReviewModel.is_active == True)
    result = await db.scalars(stmt)
    reviews = result.all()
    return reviews


@router.get("/products/{product_id}/reviews/",
            response_model=list[ReviewSchema])
async def read_review(product_id: int,
                      db: AsyncSession = Depends(get_async_db)):
    """
    Получение отзывов по переданному ID продукта.
    :param review_id:
    :param db:
    :return:
    """
    stmt = select(ProductModel).where(ProductModel.id == product_id, ProductModel.is_active == True)
    result = await db.scalars(stmt)
    product = result.first()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Product not found")

    stmt = select(ReviewModel).where(ReviewModel.product_id == product_id, ReviewModel.is_active == True)
    result = await db.scalars(stmt)
    reviews = result.all()
    return reviews


@router.post("/",
             response_model=ReviewSchema)
async def create_review(review: ReviewCreate,
                        db: AsyncSession = Depends(get_async_db),
                        current_user: UserModel = Depends(get_current_buyer)):
    """
    Добавление нового отзыва к товару
    :param review:
    :param current_user:
    :return:
    """
    stmt = select(ProductModel).where(ProductModel.id == review.product_id, ProductModel.is_active == True)
    result = await db.scalars(stmt)
    product = result.first()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Product not found")

    stmt = select(ReviewModel).where(ReviewModel.user_id == current_user.id,
                                     ReviewModel.is_active == True,
                                     ReviewModel.product_id == review.product_id)
    result = await db.scalars(stmt)
    check_review = result.first()
    if check_review:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Review is alive")

    db_review = ReviewModel(**review.model_dump(), user_id = current_user.id)
    db.add(db_review)
    await db.commit()
    await update_product_rating(db, product.id)
    await db.refresh(db_review)

    return db_review


@router.delete("/{review_id}")
async def delete_review(review_id: int,
                        db: AsyncSession = Depends(get_async_db),
                        current_user: UserModel = Depends(get_current_buyer)):
    """
    Мягкое удаление отзыва
    :param review_id:
    :param db:
    :return:
    """
    stmt = select(ReviewModel).where(ReviewModel.id == review_id, ReviewModel.is_active == True)
    result = await db.scalars(stmt)
    review = result.first()
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Review not found or inactive")

    if review.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You can only delete your own reviews")

    await db.execute(update(ReviewModel).where(ReviewModel.id == review_id).values(is_active=False))
    await db.commit()
    await update_product_rating(db, review.product_id)
    await db.refresh(review)