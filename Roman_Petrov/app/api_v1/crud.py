"""
Create
Read
Update
Delete
"""
import json
from sqlalchemy import select, update
from sqlalchemy.future import select as select_future
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.utils import logger
from app.core.models.record import Record
from app.core.shemas import (
    CreateRecord,
    ProjectMapping,
    UpdateDoTranscriptionRecord,
    UpdatePredictsRecord,
    UpdateRecord,
    UpdateResultIsGivenRecord,
    UpdateTranscriptionRecord,
    RecordBase,
)


async def get_all_records(session: AsyncSession) -> list[RecordBase]:
    stmt = select(Record).order_by(Record.id)
    result: Result = await session.execute(stmt)
    records = result.scalars().all()
    return list(records)


async def get_records_by_project_id(
    session: AsyncSession, project_id: int
) -> list[Record]:
    stmt = select(Record).where(Record.project_id == project_id)
    result: Result = await session.execute(stmt)
    records = result.scalars().all()
    return list(records)


async def get_record_by_call_session_async(
    session: AsyncSession, call_session: int
) -> Record | None:
    stmt = select(Record).where(Record.call_session == call_session)
    result: Result = await session.execute(stmt)
    return result.scalar_one_or_none()


def get_record_by_call_session(session: Session, call_session: int) -> Record | None:
    stmt = select(Record).filter_by(call_session=call_session)
    result: Result = session.execute(stmt)
    return result.one_or_none()


async def create_record(session: AsyncSession, record_in: CreateRecord) -> Record:
    record = Record(**record_in)
    session.add(record)
    await session.commit()
    return record


async def create_records(session: AsyncSession, record_in: CreateRecord) -> Record:
    record = Record(**record_in)
    session.add(record)
    await session.flush()
    return record


async def update_record_by_call_session(
    session: AsyncSession,
    record: Record,
    update_record: UpdateRecord
    | UpdateTranscriptionRecord
    | UpdatePredictsRecord
    | UpdateResultIsGivenRecord
    | UpdateDoTranscriptionRecord,
) -> Record:
    for key, value in update_record.model_dump().items():
        setattr(record, key, value)
    await session.commit()
    return record


async def delete_record_by_call_session(
    session: AsyncSession,
    record: Record,
) -> None:
    await session.delete(record)
    await session.commit()


async def get_projects_all() -> dict[str, str]:
    with open(settings.json_projects_id_name, "r") as json_file:
        data = json.load(json_file)
    return data


async def post_projects(projects=dict[str, str]) -> dict[str, str]:
    # Сохраняем словарь {"project_id": "project_name"} в json файл
    with open(settings.json_projects_id_name, "w") as json_file:
        json.dump(projects, json_file, ensure_ascii=False, indent=2)
    # Обновляем данные словаря для сопоставления project_id и project_name
    ProjectMapping.update_mapping_from_file(updated_data=projects)
    return projects


async def get_records_for_predict(session=AsyncSession) -> list[Record]:
    stmt = (
        select_future(Record)
        .where(Record.predict_model_1 == None)
        .where(Record.do_transcription == True)
        # .where(Record.predict_model_2 == None)
    )
    result: Result = await session.execute(stmt)
    records = result.scalars().all()
    return list(records)


async def get_records_for_transcription(session=AsyncSession) -> list[Record]:
    stmt = select(Record).where(Record.do_transcription == False)
    result: Result = await session.execute(stmt)
    records = result.scalars().all()
    return list(records)


async def get_records_new_predicted(session=AsyncSession) -> list[Record]:
    stmt = (
        update(Record)
        .where(Record.predict_model_1 != None)
        .where(Record.result_is_given == False)
        .values(result_is_given=True)
        .returning(Record)
        # .where(Record.predict_model_2 != None)
    )
    result: Result = await session.execute(stmt)
    records = result.scalars().all()
    return list(records)


async def get_records_all_predicted(session=AsyncSession) -> list[Record]:
    stmt = (
        select(Record)
        .where(Record.predict_model_1 != None)
        .where(Record.result_is_given == True)
        # .where(Record.predict_model_2 != None)
    )
    result: Result = await session.execute(stmt)
    records = result.scalars().all()
    return list(records)


def get_records_for_predict_sync(session: Session) -> list[Record]:
    stmt = (
        select(Record)
        .where(Record.predict_model_1 == None)
        .where(Record.do_transcription == True)
        # .where(Record.predict_model_2 == None)
    )
    result: Result = session.execute(stmt)
    records = result.all()
    logger.info(f"records for predict: {len(records)}")
    records_to_predict = [record_data[0] for record_data in records]
    return records_to_predict


def get_records_to_transcribe(session: Session) -> list[Record]:
    session.expire_all()
    stmt = select(Record).where(Record.do_transcription == False)
    # Добавляем вывод для отладки
    result: Result = session.execute(stmt)
    records = result.all()
    logger.info(f"records to transcribe: {len(records)}")
    records_to_transcribe = [record_data[0] for record_data in records]
    return records_to_transcribe
