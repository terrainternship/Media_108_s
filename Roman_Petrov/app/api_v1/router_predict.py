from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.models.db_helper import db_helper
from app.api_v1 import crud
from app.core.shemas import RecordBase
from app.core.utils import logger

router = APIRouter(tags=["Predict"])


@router.get(
    "/records_for_predict",
    status_code=status.HTTP_200_OK,
    response_model=list[RecordBase],
)
async def get_records_for_predict(
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    try:
        logger.info("Собираем записи доступные для предикта")

        # Вызываем функцию из crud для получения записей
        records = await crud.get_records_for_predict(session=session)

        # Логируем успешное выполнение эндпоинта
        logger.info("Записи доступные для предикта собраны")

        return records
    except HTTPException as e:
        # Логируем HTTP исключение
        logger.error(f"HTTP Exception: {e.detail}")
        raise e
    except Exception as e:
        # Логируем исключение, если произошла ошибка
        logger.error(f"Произошла ошибка при сборе записей доступных для предикта: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
