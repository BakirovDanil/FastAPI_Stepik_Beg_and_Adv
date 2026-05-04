from fastapi import FastAPI, Path
import uvicorn

app = FastAPI()

@app.get("/user/{username}/{age}")
async def login(username: str = Path(min_length=3,
                                     max_length=15,
                                     description="Введите имя пользователя",
                                     examples=["Ilya"]),
                age: int = Path(ge =0,
                                le =100,
                                description = "Введите возраст")) -> dict:
    return {"user": username, "age": age}

if __name__ == "__main__":
    uvicorn.run("main:app", host = "localhost", port = 8092, reload = True)