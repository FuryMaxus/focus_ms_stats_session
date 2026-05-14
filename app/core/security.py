import os
from litestar.connection import ASGIConnection
from litestar.security.jwt import JWTAuth, Token
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "clave_por_defecto_muy_insegura")

async def retrieve_user_handler(
        token: Token,
        connection: ASGIConnection
    ) -> str:
    return token.sub

jwt_auth = JWTAuth[str](
    retrieve_user_handler=retrieve_user_handler,
    token_secret=SECRET_KEY,
    exclude=["/health"] 
)