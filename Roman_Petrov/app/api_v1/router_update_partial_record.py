from fastapi import APIRouter, Depends, HTTPException, status
from app.api_v1 import crud
from app.core.shemas import (
    RecordBase,
    UpdateDoTranscriptionRecord,
    UpdatePredictsRecord,
    UpdateResultIsGivenRecord,
    UpdateTranscriptionRecord,
)
from app.core.models.db_helper import db_helper
from app.core.dependencies import record_by_call_session_async
from app.core.utils import logger
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["Update Partial Record"])


@router.patch(
    "/{call_session}/transcription/",
    response_model=RecordBase,
    status_code=status.HTTP_200_OK,
)
async def update_transcription_record_by_call_session(
    update_record: UpdateTranscriptionRecord,
    record: RecordBase = Depends(record_by_call_session_async),
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    try:
        logger.info(
            f"Обновляем транскрипцию для записи с call_session {record.call_session}"
        )

        # Вызываем функцию из crud для обновления транскрипции записи
        updated_record = await crud.update_record_by_call_session(
            session=session,
            record=record,
            update_record=update_record,
        )

        # Логируем успешное выполнение эндпоинта
        logger.info(
            f"Транскрипция для записи с call_session {record.call_session} успешно обновлена"
        )

        return updated_record
    except Exception as e:
        # Логируем исключение, если произошла ошибка
        logger.error(
            f"Произошла ошибка при обновлении транскрипции для записи с call_session {record.call_session}: {e}"
        )

        # Возвращаем HTTP исключение с кодом 500 и деталями об ошибке
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.patch(
    "/{call_session}/predicts/",
    response_model=RecordBase,
    status_code=status.HTTP_200_OK,
)
async def update_predicts_record_by_call_session(
    update_record: UpdatePredictsRecord,
    record: RecordBase = Depends(record_by_call_session_async),
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    try:
        logger.info(
            f"Обновляем predicts для записи с call_session {record.call_session}"
        )

        # Вызываем функцию из crud для обновления предсказаний записи
        updated_record = await crud.update_record_by_call_session(
            session=session,
            record=record,
            update_record=update_record,
        )

        # Логируем успешное выполнение эндпоинта
        logger.info(
            f"Predicts для записи с call_session {record.call_session} успешно обновлены"
        )

        return updated_record
    except Exception as e:
        # Логируем исключение, если произошла ошибка
        logger.error(
            f"Произошла ошибка при обновлении predicts для записи с call_session {record.call_session}: {e}"
        )

        # Возвращаем HTTP исключение с кодом 500 и деталями об ошибке
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.patch(
    "/{call_session}/result_is_given/",
    response_model=RecordBase,
    status_code=status.HTTP_200_OK,
)
async def update_result_is_given_record_by_call_session(
    update_record: UpdateResultIsGivenRecord,
    record: RecordBase = Depends(record_by_call_session_async),
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    try:
        logger.info(
            f"Обновляем result_is_given для записи с call_session {record.call_session}"
        )

        # Вызываем функцию из crud для обновления результата
        updated_record = await crud.update_record_by_call_session(
            session=session,
            record=record,
            update_record=update_record,
        )

        # Логируем успешное выполнение функции
        logger.info(
            f"Result_is_given для записи с call_session {record.call_session} успешно обновлено"
        )

        return updated_record
    except Exception as e:
        # Логируем исключение, если произошла ошибка
        logger.error(
            f"Произошла ошибка при обновлении result_is_given для записи с call_session {record.call_session}: {e}"
        )

        # Возвращаем HTTP исключение с кодом 500 и деталями об ошибке
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.patch(
    "/{call_session}/do_transcription/",
    response_model=RecordBase,
    status_code=status.HTTP_200_OK,
)
async def update_do_transcription_record_by_call_session(
    update_record: UpdateDoTranscriptionRecord,
    record: RecordBase = Depends(record_by_call_session_async),
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    try:
        logger.info(
            f"Обновляем do_transcription для записи с call_session {record.call_session}"
        )

        # Вызываем функцию из crud для обновления флага do_transcription
        updated_record = await crud.update_record_by_call_session(
            session=session,
            record=record,
            update_record=update_record,
        )

        # Логируем успешное выполнение функции
        logger.info(
            f"Do_transcription для записи с call_session {record.call_session} успешно обновлена"
        )

        return updated_record
    except Exception as e:
        # Логируем исключение, если произошла ошибка
        logger.error(
            f"Произошла ошибка при обновлении do_transcription для записи с call_session {record.call_session}: {e}"
        )

        # Возвращаем HTTP исключение с кодом 500 и деталями об ошибке
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
