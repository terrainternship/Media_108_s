from sqlite3 import IntegrityError
from fastapi import APIRouter, HTTPException, status, Depends
from app.api_v1 import crud
from app.core.shemas import (
    RecordBase,
    UpdateRecord,
)
from app.core.utils import get_record_data, logger
from app.core.models.db_helper import db_helper
from app.core.dependencies import record_by_call_session_async
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["Records"])


@router.get("/", response_model=list[RecordBase], status_code=status.HTTP_200_OK)
async def get_all_records(
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    try:
        logger.info("Получаем все записи из бд")

        # Вызываем функцию из crud для получения всех записей
        records = await crud.get_all_records(session=session)

        # Логируем успешное выполнение эндпоинта
        logger.info("Все записи успешно получены из бд")

        return records
    except Exception as e:
        # Логируем исключение, если произошла ошибка
        logger.error(f"Произошла ошибка при получении всех записей из бд: {e}")

        # Возвращаем HTTP исключение с кодом 500 и деталями об ошибке
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.get(
    "/project_id/{project_id}/",
    response_model=list[RecordBase],
    status_code=status.HTTP_200_OK,
)
async def get_records_by_project_id(
    project_id: int,
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    try:
        logger.info(f"Получаем все записи из бд по project_id {project_id}")

        # Вызываем функцию из crud для получения записей по project_id
        records = await crud.get_records_by_project_id(
            session=session, project_id=project_id
        )

        # Проверяем, есть ли записи
        if records:
            # Логируем успешное выполнение эндпоинта
            logger.info(f"Записи успешно получены из бд по project_id {project_id}")
            return records

        # Если записи отсутствуют, выбрасываем HTTP исключение 404
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project_id {project_id} not found!",
        )
    except Exception as e:
        # Логируем исключение, если произошла ошибка
        logger.error(
            f"Произошла ошибка при получении записей из бд по project_id {project_id}: {e}"
        )

        # Возвращаем HTTP исключение с кодом 500 и деталями об ошибке
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.get(
    "/{call_session}/",
    response_model=RecordBase,
    status_code=status.HTTP_200_OK,
)
async def get_record_by_call_session(
    record: RecordBase = Depends(record_by_call_session_async),
):
    try:
        logger.info(f"Получаем запись из бд по call_session {record.call_session}")

        # Возвращаем запись
        return record
    except Exception as e:
        # Логируем исключение, если произошла ошибка
        logger.error(
            f"Произошла ошибка при получении из бд записи по call_session {record.call_session}: {e}"
        )

        # Возвращаем HTTP исключение с кодом 500 и деталями об ошибке
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.get(
    "/new_predicted_records",
    response_model=list[RecordBase],
    status_code=status.HTTP_200_OK,
)
async def get_new_predicted_records(
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    try:
        logger.info("Получаем новые записи с предиктами")

        # Вызываем функцию из crud для получения новых предсказанных записей
        records = await crud.get_records_new_predicted(session=session)

        # Логируем успешное выполнение эндпоинта
        logger.info("Новые записи с предиктами успешно получены")

        return records
    except Exception as e:
        # Логируем исключение, если произошла ошибка
        logger.error(
            f"Произошла ошибка при получении из бд новых записей с пердиктами: {e}"
        )

        # Возвращаем HTTP исключение с кодом 500 и деталями об ошибке
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.get(
    "/all_predicted_records",
    response_model=list[RecordBase],
    status_code=status.HTTP_200_OK,
)
async def get_all_predicted_records(
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    try:
        logger.info("Получаем все записи с предиктами")
        # Вызываем функцию из crud для получения всех предсказанных записей
        records = await crud.get_records_all_predicted(session=session)
        logger.info("Все записи с предиктами успешно получены")
        return records
    except Exception as e:
        # Логируем исключение, если произошла ошибка
        logger.error(f"Произошла ошибка при получении всех записей с предиктами: {e}")
        # Возвращаем HTTP исключение с кодом 500 и деталями об ошибке
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.post(
    "/create_record/", response_model=RecordBase, status_code=status.HTTP_201_CREATED
)
async def create_record(
    record_in: dict,
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    try:
        logger.info("Создаем новую запись")

        # Забираем необходимые ключи и значения из пришедшего словаря
        record_data = get_record_data(record_in)

        # Проверяем существует ли запись с таким call_session
        call_session = record_data.get("call_session")
        existing_record = await crud.get_record_by_call_session_async(
            session=session,
            call_session=call_session,
        )
        # Если запись с таким call_session существует, то возвращаем её
        if existing_record:
            # Логируем, что запись уже существует
            logger.info(f"Запись с call_session {call_session} уже существует.")
            return existing_record

        # Создаем новую запись в бд и возвращаем её
        new_record = await crud.create_record(session=session, record_in=record_data)

        # Логируем успешное создание записи
        logger.info(f"Запись с call_session {call_session} успешно создана")

        return new_record
    except IntegrityError as e:
        # Check if the error is due to a unique constraint violation
        if "UNIQUE constraint failed: records.call_session" in str(e):
            # Handle the case where the call_session is not unique (e.g., log or update existing record)
            logger.error(f"IntegrityError: {e}")
        else:
            # If the error is due to a different reason, re-raise the exception
            raise e


@router.post(
    "/create_records/",
    response_model=list[RecordBase],
    status_code=status.HTTP_201_CREATED,
)
async def create_records(
    records_in: list[dict],
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    try:
        # Логируем начало выполнения эндпоинта
        logger.info("Создаем новые записи")

        created_records = []

        # Забираем все записи records из бд
        all_records = await crud.get_all_records(session=session)
        # Создаем множество из существующих call_session для быстрого поиска
        existing_call_sessions = {record.call_session for record in all_records}

        for record_in in records_in:
            # Забираем необходимые ключи и значения из пришедшего словаря
            record_data = get_record_data(record_in)
            call_session = record_data.get("call_session")
            # Проверяем есть ли пришедшая запись в бд по call_session
            if call_session in existing_call_sessions:
                # Если запись уже есть, то достаем ее из загруженных ранее данных
                existing_record = next(
                    record
                    for record in all_records
                    if record.call_session == call_session
                )
                created_records.append(existing_record)

            else:
                try:
                    # Создаем новую запись в бд
                    new_record = await crud.create_records(
                        session=session,
                        record_in=record_data,
                    )
                    created_records.append(new_record)
                except IntegrityError as e:
                    # Check if the error is due to a unique constraint violation
                    if "UNIQUE constraint failed: records.call_session" in str(e):
                        # Handle the case where the call_session is not unique
                        # (e.g., log the error, update existing record, or take other actions)
                        logger.error(f"IntegrityError: {e}")
                    else:
                        # If the error is due to a different reason, re-raise the exception
                        raise e

        # Логируем успешное выполнение эндпоинта
        logger.info("Новые записи успешно созданы")

        await session.commit()
        return created_records
    except Exception as e:
        # Логируем исключение, если произошла ошибка
        logger.error(f"Произошла ошибка при создании записей: {e}")

        # Возвращаем HTTP исключение с кодом 500 и деталями об ошибке
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
    finally:
        await session.close()


@router.put(
    "/{call_session}/", response_model=RecordBase, status_code=status.HTTP_200_OK
)
async def update_full_record_by_call_session(
    update_record: UpdateRecord,
    record: RecordBase = Depends(record_by_call_session_async),
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    try:
        logger.info(f"Обновляем запись с call_session {record.call_session}")

        # Вызываем функцию из crud для обновления записи
        updated_record = await crud.update_record_by_call_session(
            session=session, record=record, update_record=update_record
        )
        logger.info(f"Запись с call_session {record.call_session} успешно обновлена")

        return updated_record
    except Exception as e:
        # Логируем исключение, если произошла ошибка
        logger.error(
            f"Произошла ошибки при обновлении записи с call_session {record.call_session}: {e}"
        )

        # Возвращаем HTTP исключение с кодом 500 и деталями об ошибке
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.delete("/{call_session}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_record_by_call_session(
    record: RecordBase = Depends(record_by_call_session_async),
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> None:
    try:
        logger.info(f"Удаляем запись с call_session {record.call_session}")

        # Вызываем функцию из crud для удаления записи
        await crud.delete_record_by_call_session(session=session, record=record)

        logger.info(f"Запись с call_session {record.call_session} успешно удалена")
    except Exception as e:
        # Логируем исключение, если произошла ошибка
        logger.error(
            f"Произошла ошибка при удалении записи с call_session {record.call_session}: {e}"
        )

        # Возвращаем HTTP исключение с кодом 500 и деталями об ошибке
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
