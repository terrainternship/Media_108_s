from typing import Annotated
from fastapi import Depends, HTTPException, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from app.api_v1 import crud
from app.core.models.db_helper import db_helper
from app.core.shemas import RecordBase
from app.core.utils import logger


async def record_by_call_session_async(
    call_session: Annotated[int, Path],
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> RecordBase:
    try:
        logger.info(
            f"Выполнение record_by_call_session_async с call_session: {call_session}"
        )
        record = await crud.get_record_by_call_session_async(
            session=session,
            call_session=call_session,
        )
        if record:
            logger.info(f"Запись найдена для call_session: {call_session}")
            return record
        else:
            logger.warning(f"Запись не найдена для call_session: {call_session}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Запись для call_session {call_session} не найдена!",
            )
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")
        raise
