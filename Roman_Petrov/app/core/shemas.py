from datetime import datetime
import json
from typing import Optional
from pydantic import BaseModel, validator
from app.core.config import settings
from app.core.utils import remove_braces, logger


class ProjectMapping:
    PROJECT_ID_MAPPING: dict[int, str] = {}

    @classmethod
    def load_mapping_from_file(cls):
        try:
            logger.info("Загружаем ProjectMapping из файла")
            with open(settings.json_projects_id_name, "r") as json_file:
                cls.PROJECT_ID_MAPPING = json.load(json_file)
            logger.info("ProjectMapping успешно загружен")
        except FileNotFoundError:
            logger.error(f"Файл {settings.json_projects_id_name} не найден!")
            raise
        except json.JSONDecodeError:
            # Если возникает ошибка при декодировании JSON, также оставляем текущий словарь
            logger.error(f"Что-то случилось с файлом {settings.json_projects_id_name}")
            raise

    @classmethod
    def update_mapping_from_file(cls, updated_data: dict[str, str]):
        try:
            logger.info("Обновляем ProjectMapping из файла")
            # Удаляем ключи, которых нет в updated_data
            keys_to_remove = set(cls.PROJECT_ID_MAPPING.keys()) - set(
                updated_data.keys()
            )
            for key in keys_to_remove:
                cls.PROJECT_ID_MAPPING.pop(key, None)

            # Обновляем словарь на основе переданных данных
            cls.PROJECT_ID_MAPPING.update(updated_data)
            logger.info("ProjectMapping  успешно обновлен")
        except Exception as e:
            # Логируем исключение, если оно произошло
            logger.error(f"Возникла ошибка при обновлении ProjectMapping: {e}")
            raise


class CreateRecord(BaseModel):
    id: Optional[int] = None
    predict_model_1: Optional[int] = None
    # predict_model_2: Optional[int] = None
    result_is_given: Optional[bool] = None
    do_transcription: Optional[bool] = None
    create_date: Optional[datetime] = None


class RecordBase(CreateRecord):
    project_id: Optional[int] = None
    project_name: Optional[str] = None
    path_to_audio: Optional[str] = None
    status: Optional[str] = None
    type: Optional[str] = None
    site: Optional[str] = None
    type_visitor: Optional[str] = None
    scenario: Optional[str] = None
    operations: Optional[str] = None
    type_device: Optional[str] = None
    first_advertising_campaign: Optional[str] = None
    net_conversation_duration: Optional[int] = None
    request_number: Optional[float] = None
    visitor_id: Optional[int] = None
    call_session: Optional[int] = None
    transcription_text: Optional[str] = None

    @validator("net_conversation_duration", pre=True, always=True)
    def convert_duration_to_seconds(cls, value):
        try:
            if isinstance(value, str):
                # Assuming the format HH:MM:SS
                hours, minutes, seconds = map(int, value.split(":"))
                return hours * 3600 + minutes * 60 + seconds
            return value
        except Exception as e:
            # Логируем исключение, если произошла ошибка при конвертации длительности
            logger.error(f"Возникла ошибка при конвертации длительности звонка: {e}")
            raise

    @validator("project_name", pre=True, always=True)
    def map_project_id_to_name(cls, value, values):
        try:
            project_id = values.get("project_id")
            if project_id is not None:
                project_id_str = str(project_id)
                # Получить значение из словаря сопоставления
                return ProjectMapping.PROJECT_ID_MAPPING.get(project_id_str, value)
            return value
        except Exception as e:
            # Логируем исключение, если произошла ошибка при сопоставлении проекта по идентификатору
            logger.error(
                f"Возникла ошибка при сопоставлении ProjectMapping (идентификатора и названия проекта): {e}"
            )
            raise

    @validator(
        "status",
        "type",
        "site",
        "type_visitor",
        "scenario",
        "operations",
        "type_device",
        "first_advertising_campaign",
        pre=True,
        always=True,
    )
    def clean_string_values(cls, value):
        try:
            if isinstance(value, str):
                return remove_braces(value)
            return value
        except Exception as e:
            # Логируем исключение, если произошла ошибка при очистке строкового значения
            logger.error(f"Произошла ошибка при очистке строкового значения: {e}")
            raise


class UpdateRecord(RecordBase):
    pass


class UpdateTranscriptionRecord(BaseModel):
    transcription_text: str = None


class UpdatePredictsRecord(BaseModel):
    predict_model_1: int = None
    # predict_model_2: int = None


class UpdateResultIsGivenRecord(BaseModel):
    result_is_given: bool = None


class UpdateDoTranscriptionRecord(BaseModel):
    do_transcription: bool = None


class ResponseRecord(RecordBase):
    call_session: int
    whisper_text: str
    predict: int
