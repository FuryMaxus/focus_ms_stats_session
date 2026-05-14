import os
from advanced_alchemy.extensions.litestar import SQLAlchemyPlugin, SQLAlchemyAsyncConfig

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://neondb_owner:npg_r8JF6hvYTiAe@ep-noisy-waterfall-apfyr0n0.c-7.us-east-1.aws.neon.tech/neondb?sslmode=require"
)
db_config = SQLAlchemyAsyncConfig(
    connection_string= DATABASE_URL
)

db_plugin = SQLAlchemyPlugin(config=db_config)