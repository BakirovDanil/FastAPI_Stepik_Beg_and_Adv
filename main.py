from fastapi import FastAPI, Path, Body, status, HTTPException
import uvicorn
from typing import Annotated

app = FastAPI()

messages_db = {0: "First post in FastAPI"}

@app.get("/messages/{message_id}")
async def read_message(message_id: Annotated[int, Path()]) -> str:
    """
    Функция получения конкретной записи по id
    :param message_id:
    :return:
    """
    try:
        return messages_db[message_id]
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

@app.get("/messages")
async def read_messages() -> dict:
    """
    Функция получения всех записей
    :return:
    """
    return messages_db

@app.post("/messages", status_code=status.HTTP_201_CREATED)
async def create_message(message: Annotated[str, Body(...)]) -> str:
    """
    Функция создания сообщения
    :param message:
    :return:
    """
    current_index = max(messages_db) + 1 if messages_db else 0
    messages_db[current_index] = message
    return "Message created!"

@app.put("/messages/{message_id}", status_code=status.HTTP_200_OK)
async def update_message(message_id: int,
                         message: Annotated[str, Body(...)]) -> str:
    if message_id not in messages_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Message not found")
    messages_db[message_id] = message
    return "Message updated!"

@app.delete("/messages/{message_id}", status_code=status.HTTP_200_OK)
async def delete_message(message_id: int) -> str:
    if message_id not in messages_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    messages_db.pop(message_id)
    return f"Message ID={message_id} deleted!"


if __name__ == "__main__":
    uvicorn.run("main:app", host = "localhost", port = 8092, reload = True)