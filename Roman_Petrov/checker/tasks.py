import json
import requests
from app.api_v1.crud import (
    get_records_for_predict_sync,
    get_records_to_transcribe,
    get_record_by_call_session,
)
from requests.exceptions import ConnectionError
from app.core.predict_model_1 import get_predict_model_1
from app.core.utils import clean_text, logger
from json import JSONEncoder
from datetime import datetime
from checker.celery import celery_app
from app.core.models.db import db_session
from tqdm import tqdm
import redis
from app.core.config import settings


class DateTimeEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)


redis_client = redis.StrictRedis(
    host=settings.redis_host, port=settings.redis_port, db=1
)


records_key = "records_for_transcribe"
try:
    redis_client.delete(records_key)
    logger.info(f"Cleared Redis set with key: {records_key}")
except Exception as e:
    logger.error(
        f"An error occurred while clearing Redis set with key {records_key}: {e}"
    )


@celery_app.task(expires=5)
def check():
    try:
        # Получаем записи для транскрипции из Redis
        records_for_transcribe = [
            json.loads(record) for record in redis_client.smembers(records_key)
        ]

        if not records_for_transcribe:
            # Если список пуст, запускаем асинхронную задачу для пополнения списка
            check_records.apply_async()
            result = "Пополняем список аудиозаписей для транскрипции"
        else:
            result = "Список обработки аудио еще не освободился"

        return result
    except Exception as e:
        # Логируем исключение, если произошла ошибка
        logger.error(f"An error occurred while executing the 'check' task: {e}")

        # Возвращаем сообщение об ошибке
        return "An error occurred during the 'check' task execution."


@celery_app.task
def update_predicts_for_records():
    try:
        with db_session() as session:
            records_to_predict = get_records_for_predict_sync(session=session)
            if records_to_predict:
                predicts = get_predict_model_1(records_to_predict)
                # Сопоставление по идентификатору сессии звонка
                records_dict = {
                    record.call_session: record for record in records_to_predict
                }
                for modified_record in predicts:
                    call_session = modified_record["Идентификатор сессии звонка"]
                    if call_session in records_dict:
                        record = records_dict[call_session]
                        record.predict_model_1 = modified_record["y_pred"]
                        # record.predict_model_2 = 0
                session.commit()
                return "predict моделей обновлен"
            return "На predict нет доступных записей"
    except Exception as e:
        # Логируем исключение, если произошла ошибка
        logger.error(
            f"An error occurred while executing the 'update_predicts_for_records' task: {e}"
        )

        # Возвращаем сообщение об ошибке
        return (
            "An error occurred during the 'update_predicts_for_records' task execution."
        )


@celery_app.task(expires=5)
def check_records():
    try:
        with db_session() as session:
            records_to_transcribe = get_records_to_transcribe(session=session)
            records_for_transcribe = []
            if records_to_transcribe:
                for record in records_to_transcribe[:2]:
                    call_session = str(record.call_session)
                    path_to_audio = record.path_to_audio

                    # Проверяем, была ли запись уже обработана
                    if call_session not in [
                        rec["call_session"] for rec in records_for_transcribe
                    ]:
                        # Создаем словарь с нужными значениями
                        record_data = {
                            "call_session": call_session,
                            "path_to_audio": path_to_audio,
                        }

                        # Преобразуем словарь в JSON-строку и добавляем в Redis
                        redis_client.sadd(records_key, json.dumps(record_data))
                        result_message = "Записи добавлены в список для транскрипции"
                    else:
                        result_message = "Нет новых записей для транскрипции"
            else:
                result_message = "Нет доступных записей для транскрипции"
            transcribe.apply_async()
            return result_message
    except Exception as e:
        # Логируем исключение, если произошла ошибка
        logger.error(f"An error occurred while executing the 'check_records' task: {e}")

        # Возвращаем сообщение об ошибке
        return "An error occurred during the 'check_records' task execution."


@celery_app.task(expires=300)
def transcribe():
    try:
        records_for_transcribe = [
            json.loads(record) for record in redis_client.smembers(records_key)
        ]
        if records_for_transcribe:
            for record in tqdm(records_for_transcribe, desc="Transcribing Records"):
                call_session = record["call_session"]
                audio_data = record["path_to_audio"]

                try:
                    task_result = process_and_save_audio.apply_async(
                        args=[audio_data],
                        link=process_result.s(
                            call_session=call_session,
                        ),
                    )
                except Exception as e:
                    # Логирование ошибки
                    logger.error(f"Error processing audio for {call_session}: {e}")
                    # Продолжаем с следующей записью
                    continue
            result_message = "Все записи отправлены на транскрипцию"
        else:
            result_message = "Все записи из списка уже обработаны"
        return result_message
    except Exception as e:
        # Логируем исключение, если произошла ошибка
        logger.error(f"An error occurred while executing the 'transcribe' task: {e}")

        # Возвращаем сообщение об ошибке
        return "An error occurred during the 'transcribe' task execution."


@celery_app.task(expires=300)
def process_result(result, call_session):
    try:
        if result is not None:
            with db_session() as session:
                record = get_record_by_call_session(
                    session=session, call_session=call_session
                )
                if record:
                    record = record[0]
                    clean_result = clean_text(result)
                    # Обновите данные в созданном экземпляре
                    record.transcription_text = clean_result
                    record.do_transcription = True
                    session.commit()
                    # Удаляем обработанную запись из списка
                    call_session_to_remove = str(record.call_session)
                    path_to_audio = record.path_to_audio

                    json_record_to_remove = json.dumps(
                        {
                            "call_session": call_session_to_remove,
                            "path_to_audio": path_to_audio,
                        }
                    )
                    redis_client.srem(records_key, json_record_to_remove)
                    logger.info(
                        f"Запись call_session {record.call_session} обработана и удалена из списка records_for_transcribe"
                    )
                    return f"Транскрипция для {record.call_session} была обновлена!"
                else:
                    return f"Запись с call_session={record.call_session} не найдена."
        else:
            return None
    except Exception as e:
        # Логируем исключение, если произошла ошибка
        logger.error(
            f"An error occurred while executing the 'process_result' task: {e}"
        )

        # Возвращаем сообщение об ошибке
        return e


@celery_app.task(expires=300)
def process_and_save_audio(audio_data):
    try:
        logger.info(f"Processing audio file: {audio_data}")

        container_address = process_and_save_audio.app.conf.container_address
        container_ports = process_and_save_audio.app.conf.container_ports

        while True:
            for port in container_ports:
                container_url = f"http://{container_address}:{port}"
                # Логируем информацию о текущей попытке отправки аудио
                logger.info(f"Processing audio file: {container_url}")

                # Проверяем статус код HTTP
                status_code = check_http_status_code(container_url)

                if status_code == 200:
                    # Если статус код успешен, обрабатываем аудио
                    result = process_audio(audio_data, container_url)
                    logger.info(f"Audio file sent to: {container_url}")
                    return result

    except Exception as e:
        # Логируем исключение, если произошла ошибка
        logger.error(f"An error occurred while processing audio: {e}")

        # Возвращаем None в случае ошибки
        return None


def check_http_status_code(url, timeout=5):
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code
    except requests.exceptions.RequestException as e:
        logger.error(f"Error making request: {e}")
        return None


def process_audio(audio_data, container_url):
    # Предположим, что у вас есть endpoint на контейнере для обработки аудио
    api_endpoint = f"{container_url}/asr"
    # Параметры запроса
    params = {
        "encode": False,
        "task": "transcribe",
        "language": "ru",
        "initial_prompt": None,
        "vad_filter": False,
        "word_timestamps": False,
        "output": "txt",
    }
    # Передайте данные на контейнер с использованием HTTP POST запроса
    files = {"audio_file": ("audio_file.wav", open(audio_data, "rb"), "audio/wav")}

    try:
        response = requests.post(api_endpoint, data=params, files=files)
        response.raise_for_status()  # Проверка ошибок HTTP

        return response.text
    except ConnectionError as e:
        logger.error(f"Connection error: {e}")
    except requests.exceptions.HTTPError as errh:
        logger.error("HTTP Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        logger.error("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        logger.error("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        logger.error("OOps: Something went wrong", err)
