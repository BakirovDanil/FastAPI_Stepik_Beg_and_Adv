from passlib.context import CryptContext

# создание контекста для хеширования с использованием bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

def hash_password(password: str):
    """
    Преобразование пароля в хеш с использованием bcrypt.
    :param password:
    :return:
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str,
                    hashed_password: str) -> bool:
    """
    Проверят, соответствует ли введенный пароль сохраненному хешу.
    :param plain_password:
    :param hashed_password:
    :return:
    """
    return pwd_context.verify(plain_password, hashed_password)