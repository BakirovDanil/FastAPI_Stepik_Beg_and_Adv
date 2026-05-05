from fastapi import FastAPI, Path, Body, status, HTTPException
from pydantic import BaseModel
import uvicorn
from typing import Annotated

app = FastAPI()


class MessageCreate(BaseModel):
    content: str

class Message(MessageCreate):
    id: int

messages_db: list[Message] = [Message(id=0, content="First post in FastAPI")]


@app.get("/messages/{message_id}", response_model=Message)
async def read_message(message_id: Annotated[int, Path()]) -> Message:
    """
    Функция получения конкретной записи по id
    :param message_id:
    :return:
    """
    for message in messages_db:
        if message.id == message_id:
            return message
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@app.get("/messages", response_model=list[Message])
async def read_messages() -> list[Message]:
    """
    Функция получения всех записей
    :return:
    """
    return messages_db


@app.post("/messages", response_model=Message, status_code=status.HTTP_201_CREATED)
async def create_message(message_create: MessageCreate) -> Message:
    """
    Функция создания сообщения
    :param message:
    :return:
    """
    next_id = max((msg.id for msg in messages_db), default=-1) + 1
    new_message = Message(id=next_id, content=message_create.content)
    messages_db.append(new_message)
    return new_message


@app.put("/messages/{message_id}", response_model=Message, status_code=status.HTTP_200_OK)
async def update_message(message_id: int,
                         message_create: MessageCreate) -> Message:
    for i, message in enumerate(messages_db):
        if message.id == message_id:
            updated_message = Message(id=message_id, content=message_create.content)
            messages_db[i] = updated_message
            return updated_message
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")


@app.delete("/messages/{message_id}", status_code=status.HTTP_200_OK)
async def delete_message(message_id: int) -> dict:
    for i, message in enumerate(messages_db):
        if message.id == message_id:
            messages_db.pop(i)
            return {"detail": f"Message ID = {message_id} deleted!"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8092, reload=True)
