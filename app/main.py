from litestar import Litestar
from litestar.plugins.sqlalchemy import SQLAlchemyPlugin
from app.core.db_config import db_config
from app.api.v1.sessionController import SessionController

app = Litestar(
    route_handlers=[SessionController],
    plugins=[SQLAlchemyPlugin(db_config)]
)