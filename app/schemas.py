from pydantic import BaseModel, Field, ConfigDict, EmailStr
from decimal import Decimal
from datetime import datetime

class CategoryCreate(BaseModel):
    """
    Модель для создания и обновления категорий.
    Используется в POST и PUT запросах
    """
    name: str = Field(...,
                      min_length=3,
                      max_length=50,
                      description="Название категории (3-50 символов)")
    parent_id: int | None = Field(default=None,
                                  description="ID родительской категории, если есть")


class Category(CategoryCreate):
    """
    Модель для ответа с данными категории.
    Используется в GET-запросах.
    """
    id: int = Field(...,
                    description="Уникальный идентификатор категории")
    is_active: bool = Field(...,
                            description="Активность категории")

    model_config = ConfigDict(from_attributes=True)


class ProductCreate(BaseModel):
    """
    Модель для создания и обновления товара.
    Используется в POST и PUT запросах.
    """
    name: str = Field(...,
                      min_length=3,
                      max_length=100,
                      description="Название товара (3-100 символов)")
    description: str | None = Field(default=None,
                                    max_length=500,
                                    description="Описание товаров (до 500 символов)")
    price: Decimal = Field(...,
                           description="Цена товара в рублях (больше 0)",
                           gt=0,
                           decimal_places=2)
    image_url: str | None = Field(default=None,
                                  max_length=200,
                                  description="URL изображения товара")
    stock: int = Field(...,
                       ge=0,
                       description="Количество товара на складе (0 или больше)")
    category_id: int = Field(...,
                             description="ID категории, к которой относится товар")


class Product(ProductCreate):
    """
    Модель для ответа с данными товара.
    Используется в GET-запросах.
    """
    id: int = Field(...,
                    description="Уникальный идентификатор товара")
    is_active: bool = Field(...,
                            description="Активность товара")
    rating: float = Field(...,
                          description="Средняя оценка товара")

    model_config = ConfigDict(from_attributes=True)


class UserBase(BaseModel):
    """
    Базовая модель пользователя.
    """
    email: EmailStr = Field(description="Email пользователя")
    role: str = Field(default="buyer",
                      pattern="^(buyer|seller|admin)",
                      description="Роль: 'buyer' или 'seller' или 'admin'")


class UserCreate(UserBase):
    """
    Модель пользователя, используемая в POST и PUT запросах.
    """
    password: str = Field(min_length=8, description="Пароль (минимум 8 символов)")


class User(UserBase):
    """
    Модель пользователя, используемая в GET-запросах.
    """
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ReviewBase(BaseModel):
    """
    Базовая модель отзыва.
    """
    product_id: int = Field(...,
                            description="Уникальный идентификатор товара")
    comment: str | None = Field(default=None,
                                description="Содержание")
    grade: int = Field(...,
                       gt=1,
                       lt=6,
                       description="Оценка")


class ReviewCreate(ReviewBase):
    """
    Модель для создания отзыва
    """
    pass


class Review(ReviewBase):
    """
    Модель отзыва, используемая в GET-запросах.
    """
    id: int = Field(...,
                    description="Уникальный идентификатор отзыва")
    is_active: bool = Field(...,
                            description="Статус отзыва")
    user_id: int = Field(...,
                         description="ID пользователя, который оставил отзыв")
    comment_date: datetime = Field(...,
                                   description="Дата отзыва")