# Импортируем необходимые библиотеки
from fastapi import FastAPI
from app.routers import categories, products, users
import uvicorn

# Создаем приложение FastAPI
app = FastAPI(
    title="FastAPI Интернет-магазин",
    version="0.1.0"
)

# подключение маршрутов категорий и товаров
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(users.router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8092, reload=True)
