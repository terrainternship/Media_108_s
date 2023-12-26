from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api_v1.router import router as router_v1
import uvicorn
from app.core.shemas import ProjectMapping
from app.core.models.base import Base
from app.core.models.db_helper import db_helper
from app.core.config import settings
from app.core.utils import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("Starting lifespan context")

        # Загружаем маппинг проектов из файла
        ProjectMapping.load_mapping_from_file()

        # Создаем таблицы в базе данных
        async with db_helper.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        logger.info("Lifespan context started successfully")

        yield
    except Exception as e:
        # Логируем исключение, если произошла ошибка
        logger.error(f"An error occurred in the lifespan context: {e}")
        raise


app = FastAPI(lifespan=lifespan)
app.include_router(router=router_v1, prefix=settings.api_v1_prefix)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
