from datetime import datetime

from typing import Optional

from sqlalchemy import func
from app.core.models.base import Base
from sqlalchemy.orm import Mapped, mapped_column


class Record(Base):
    __tablename__ = "records"

    project_id: Mapped[int]
    project_name: Mapped[Optional[str]]
    path_to_audio: Mapped[Optional[str]] = mapped_column(default="Нет данных")
    status: Mapped[str] = mapped_column(default="Нет данных")
    type: Mapped[Optional[str]] = mapped_column(default="Нет данных")
    site: Mapped[Optional[str]] = mapped_column(default="Нет данных")
    type_visitor: Mapped[Optional[str]] = mapped_column(default="Нет данных")
    scenario: Mapped[Optional[str]] = mapped_column(default="Нет данных")
    operations: Mapped[Optional[str]] = mapped_column(default="Нет данных")
    type_device: Mapped[str] = mapped_column(default="Нет данных")
    first_advertising_campaign: Mapped[Optional[str]] = mapped_column(
        default="Нет данных"
    )
    net_conversation_duration: Mapped[int] = mapped_column(default=0)
    request_number: Mapped[int] = mapped_column(default=0)
    visitor_id: Mapped[Optional[int]] = mapped_column(default=0)
    transcription_text: Mapped[Optional[str]] = mapped_column(default="безответа")
    call_session: Mapped[Optional[int]] = mapped_column(unique=True, nullable=True)
    do_transcription: Mapped[bool] = mapped_column(default=False)
    predict_model_1: Mapped[Optional[int]] = mapped_column(nullable=True)
    # predict_model_2: Mapped[Optional[int]] = mapped_column(nullable=True)
    result_is_given: Mapped[bool] = mapped_column(default=False)
    create_date: Mapped[datetime] = mapped_column(insert_default=func.now())

    def to_dict(self):
        return {
            "project_id": self.project_id,
            "project_name": self.project_name,
            "path_to_audio": self.path_to_audio,
            "status": self.status,
            "type": self.type,
            "site": self.site,
            "type_visitor": self.type_visitor,
            "scenario": self.scenario,
            "operations": self.operations,
            "type_device": self.type_device,
            "first_advertising_campaign": self.first_advertising_campaign,
            "net_conversation_duration": self.net_conversation_duration,
            "request_number": self.request_number,
            "visitor_id": self.visitor_id,
            "transcription_text": self.transcription_text,
            "call_session": self.call_session,
            "predict_model_1": self.predict_model_1,
            # "predict_model_2": self.predict_model_2,
            "result_is_given": self.result_is_given,
            "create_date": self.create_date,
        }

    @classmethod
    def from_dict(cls, data_dict):
        return cls(
            project_id=data_dict.get("project_id"),
            project_name=data_dict.get("project_name"),
            path_to_audio=data_dict.get("path_to_audio"),
            status=data_dict.get("status"),
            type=data_dict.get("type"),
            site=data_dict.get("site"),
            type_visitor=data_dict.get("type_visitor"),
            scenario=data_dict.get("scenario"),
            operations=data_dict.get("operations"),
            type_device=data_dict.get("type_device"),
            first_advertising_campaign=data_dict.get("first_advertising_campaign"),
            net_conversation_duration=data_dict.get("net_conversation_duration"),
            request_number=data_dict.get("request_number"),
            visitor_id=data_dict.get("visitor_id"),
            transcription_text=data_dict.get("transcription_text"),
            call_session=data_dict.get("call_session"),
            predict_model_1=data_dict.get("predict_model_1"),
            # predict_model_2=data_dict.get("predict_model_2"),
            result_is_given=data_dict.get("result_is_given"),
            create_date=data_dict.get("create_date"),
        )
