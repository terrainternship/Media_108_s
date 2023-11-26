from typing import Optional, Union
from pydantic import BaseModel, validator
import re


class BaseTransformModel(BaseModel):
    class Config:
        @classmethod
        def transform(cls, value):
            call_session = cls.get_call_session(value)
            return {"call_session": call_session}

    @staticmethod
    def get_call_session(value: dict) -> Optional[int]:
        if "Имя_файла" in value:
            match = re.search(r"session_(\d*)_talk", value["Имя_файла"])
            return int(match.group(1)) if match else None
        else:
            return None

    @staticmethod
    def convert_time_to_seconds(time_str: Optional[str]) -> int:
        if isinstance(time_str, int):
            return time_str  # если уже целое число, возвращаем его без изменений
        try:
            hours, minutes, seconds = map(int, time_str.split(":"))
            return hours * 3600 + minutes * 60 + seconds
        except (AttributeError, ValueError):
            return 0  # в случае ошибки возвращаем None


class DataModel(BaseTransformModel):
    ID_проекта: int
    Имя_файла: Optional[str] = None
    Статус: Optional[str] = None
    Тип: Optional[str] = None
    Сайт: Optional[str] = None
    Тип_посетителя: Optional[str] = None
    Сценарий: Optional[str] = None
    Операции: Optional[str] = None
    Тип_устройства: Optional[str] = None
    Первая_рекламная_кампания: Optional[str] = None
    Чистая_длительность_разговора: Optional[int] = None
    Номер_обращения: Optional[float] = None
    ID_посетителя: Optional[float] = None
    whisper: Optional[str] = None
    call_session: Optional[int] = None
    predict: Optional[int] = None

    def __init__(self, **data):
        super().__init__(**data)
        self.call_session = self.get_call_session(data)

    @validator("Чистая_длительность_разговора", pre=True, always=True)
    def transform_time(cls, value):
        return cls.convert_time_to_seconds(value)

    # @validator("ID_посетителя", pre=True, always=True)
    # def parse_id_visitor(cls, value):
    #     if isinstance(value, str):
    #         return None if value.lower() == "none" else float(value)
    #     return value

    @validator("ID_посетителя", "Номер_обращения", "predict", pre=True, always=True)
    def parse_numeric_fields(cls, value):
        if isinstance(value, str):
            return None if value.lower() == "none" else float(value)
        return value


class DataOutput(BaseModel):
    call_session: Optional[int]
    predict: Optional[int]

    class Config:
        @classmethod
        def json_schema_extra(cls, schema, model):
            # Добавляем описания полей для документации
            schema["properties"]["call_session"]["description"] = "Session ID"
            schema["properties"]["predict"][
                "description"
            ] = "Prediction result (if available)"
