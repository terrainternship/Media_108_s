import pickle as pkl
import re
import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder
from app.core.config import BASE_DIR, settings
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)  # Устанавливаем уровень логирования

# Создаем обработчик для записи в файл
handler = logging.FileHandler("app_info.log", encoding="utf-8")
handler.setLevel(logging.INFO)
handler2 = logging.FileHandler("app_error.log", encoding="utf-8")
handler2.setLevel(logging.ERROR)

# Создаем форматтер для определения формата логов
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
handler2.setFormatter(formatter)

# Добавляем обработчик к логгеру
logger.addHandler(handler)
logger.addHandler(handler2)


# Загрузка токенайзера и энкодеров, необходимых для подготовки данных
try:
    with open(f"{BASE_DIR}/Materials/token_encoders.pkl", "rb") as f:
        encoders, tokenizer_txt = pkl.load(f)
except Exception as e:
    logger.error(f"Возникла проблема при загрузке токенайзера и энкодеров: {e}")
    raise


def get_record_data(data: dict) -> dict:
    try:
        # Логируем начало выполнения функции
        logger.info("Получаем данные для записи get_record_data")

        record_data = {
            "project_id": data.get("ID проекта"),
            "path_to_audio": data.get("Имя файла"),
            "status": data.get("Статус"),
            "type": data.get("Тип"),
            "site": data.get("Сайт"),
            "type_visitor": data.get("Тип посетителя"),
            "scenario": data.get("Сценарий"),
            "operations": data.get("Операции"),
            "type_device": data.get("Тип устройства"),
            "first_advertising_campaign": data.get("Первая рекламная кампания"),
            "net_conversation_duration": data.get("Чистая длительность разговора"),
            "request_number": data.get("Номер обращения"),
            "visitor_id": data.get("ID посетителя"),
            "call_session": data.get("Идентификатор сессии звонка"),
            "transcription_text": (
                data.get("whisper", "безответа")
                if data.get("whisper") != ""
                else "безответа"
            ),
        }

        # Логируем успешное выполнение функции
        logger.info("Данные для записи успешно получены")

        return record_data
    except Exception as e:
        # Логируем исключение, если произошла ошибка
        logger.error(f"Произошла ошибка при получении данных для записи: {e}")
        raise


def get_record_to_df_data(data: list) -> list:
    try:
        # Логируем начало выполнения функции
        logger.info("Конвертируем данные записи в DataFrame формат")

        records_data = []
        for record in data:
            record_data = {
                "ID проекта": record.get("project_id"),
                "Имя файла": record.get("path_to_audio"),
                "Статус": record.get("status"),
                "Тип": record.get("type"),
                "Сайт": record.get("site"),
                "Тип посетителя": record.get("type_visitor"),
                "Сценарий": record.get("scenario"),
                "Операции": record.get("operations"),
                "Тип устройства": record.get("type_device"),
                "Первая рекламная кампания": record.get("first_advertising_campaign"),
                "Чистая длительность разговора": record.get(
                    "net_conversation_duration"
                ),
                "Номер обращения": record.get("request_number"),
                "ID посетителя": record.get("visitor_id"),
                "Идентификатор сессии звонка": record.get("call_session"),
                "whisper": record.get("transcription_text"),
            }
            records_data.append(record_data)

        # Логируем успешное выполнение функции
        logger.info("Данные записи успешно сконвертированы в DataFrame формат")

        return records_data
    except Exception as e:
        # Логируем исключение, если произошла ошибка
        logger.error(
            f"Произошла ошибка при конвертации данных записи в DataFrame формат: {e}"
        )
        raise


# Функция удаления {}
def remove_braces(value):
    try:
        logger.info("Удаляем скобочки из строки")

        # Удаляем фигурные скобки из значения
        cleaned_value = value.replace("{", "").replace("}", "")

        logger.info("Скобочки удалены успешно")

        return cleaned_value
    except Exception as e:
        logger.error(f"Произошла ошибка при удалении скобочек из строки: {e}")
        raise


def clean_text(text):
    try:
        logger.info("Очищаем текст")

        # Используем регулярное выражение, чтобы оставить только русские буквы и цифры
        cleaned_text = re.sub(r"[^а-яА-Я0-9]", " ", text)

        # Проверяем, не является ли строка пустой после очистки
        if not cleaned_text.strip():
            logger.warning(
                "Текстовая строка стала пустой после очистки текста, просвоено значение 'безответа'"
            )

            return "безответа"

        # Удаляем лишние пробелы и приводим к нижнему регистру
        cleaned_text = " ".join(cleaned_text.split()).lower()

        logger.info("Текст успешно очищен")

        return cleaned_text
    except Exception as e:
        logger.error(f"Произошла ошибки при очистке текста: {e}")
        raise


def clean_text_df(data: pd.DataFrame):
    try:
        logger.info("Очищаем текст в DataFrame")

        data["whisper"] = data["whisper"].apply(clean_text)

        logger.info("Текст в DataFrame успешно очищен")

        return data
    except Exception as e:
        # Логируем исключение, если произошла ошибка
        logger.error(f"Произошла ощибки при очистке текста в DataFrame: {e}")
        raise


def text_to_bow(data: pd.DataFrame):
    try:
        logger.info("Конвертируем текст в Bag of Words (BOW)")

        # Получение матрицы BOW для колонки с расшифровками
        txt_list = data["whisper"].tolist()  # Список расшифровок звонков
        text_bow = tokenizer_txt.texts_to_matrix(txt_list)

        logger.info("Текст успешно сконвертирован в Bag of Words (BOW)")

        return text_bow
    except Exception as e:
        # Логируем исключение, если произошла ошибка
        logger.error(
            f"Произошла ошибка при конвертации текста в Bag of Words (BOW): {e}"
        )
        raise


def df_to_ohe(df, collist, lst_encoders={}):
    """
    Процедура поочередного преобразования колонок из списка через OneHotEncoder в ОНЕ
    С последующей сборкой в единый массив. Параметры:
    df - датафрейм
    collist - список колонок
    Возвращает собранный массив и список энкодеров
    """
    try:
        logger.info("Конвертируем колонки DataFrame в One-Hot Encoding (OHE)")

        create_encode = True if len(lst_encoders) == 0 else False
        list_code = []

        for i in range(len(collist)):
            if create_encode:
                logger.info(
                    f"Создаем OneHotEncoder and и конвертируем колонки {collist[i]}"
                )

                encoder = OneHotEncoder(
                    handle_unknown="infrequent_if_exist", sparse_output=False
                )
                encoder.fit(np.array(df[collist[i]].values).reshape(-1, 1))
                lst_encoders[collist[i]] = encoder
                list_code.append(
                    encoder.transform(np.array(df[collist[i]].values).reshape(-1, 1))
                )
            else:
                encoder = lst_encoders[collist[i]]
                list_code.append(
                    encoder.transform(np.array(df[collist[i]].values).reshape(-1, 1))
                )

        x_data = np.hstack(list_code)

        logger.info(
            "DataFrame колонки успешно сконвертированы в One-Hot Encoding (OHE)"
        )

        return x_data, lst_encoders
    except Exception as e:
        # Логируем исключение, если произошла ошибка
        logger.error(f"Произошла ошибка при конвертации колонок DataFrame в OHE: {e}")
        raise


def ohe_columns(data: pd.DataFrame, encoders=encoders):
    # Получение матрицы ОНЕ
    col_to_ohe = [
        "Статус",
        "Тип",
        "Сайт",
        "Тип посетителя",
        "Сценарий",
        "Операции",
        "Тип устройства",
        "Первая рекламная кампания",
    ]
    data[col_to_ohe] = data[col_to_ohe].fillna(
        "Нет данных"
    )  # Дозаполним незаполненные данные
    ohe_data, encoders = df_to_ohe(data, col_to_ohe, lst_encoders=encoders)
    ohe_data = ohe_data.astype("float32")
    return ohe_data


def time_to_seconds(data: pd.DataFrame):
    try:
        logger.info("Конвертируем время колонки в секунды")

        column_name = "Чистая длительность разговора"

        # Проверяем, существует ли колонка в DataFrame
        if column_name in data.columns:
            # Преобразуем всю колонку в секунды
            data[column_name] = data[column_name].apply(convert_duration_to_seconds)
        else:
            logger.warning(f"Колонка '{column_name}' не найдена в DataFrame.")

        logger.info(f"Время колонки {column_name} успешно сконвертировано в секунды")

        return data
    except Exception as e:
        # Логируем исключение, если произошла ошибка
        logger.error(
            f"Произошла ошибка при конвертации колонки {column_name} в секунды: {e}"
        )
        raise


def convert_duration_to_seconds(duration_str):
    try:
        logger.info(f"Конвертируем '{duration_str}' в секунды")

        # Преобразуем строку длительности (HH:MM:SS) в timedelta
        duration = pd.to_timedelta(duration_str)

        # Преобразуем timedelta в общее количество секунд (целое число)
        seconds = int(duration.total_seconds())

        # Логируем успешное выполнение функции
        logger.info(
            f"Время '{duration_str}' сконвертировано в {seconds} секунды успешно"
        )

        return seconds
    except Exception as e:
        # Логируем исключение, если произошла ошибка
        logger.error(
            f"Произошла ошибка при конвертации '{duration_str}' в секунды: {e}"
        )
        raise


def digit_cols(data: pd.DataFrame):
    try:
        # Логируем начало выполнения функции
        logger.info("Преобразование числовых колонок в DataFrame")

        # Применяем функцию time_to_seconds для преобразования временных данных
        data = time_to_seconds(data)

        # Массив из числовых колонок
        digit_col = [
            "Чистая длительность разговора",
            "Номер обращения",
            "ID посетителя",
        ]

        # Дозаполняем, если есть незаполненные данные
        data[digit_col] = data[digit_col].fillna(0)

        # Понижаем разрядность колонки для более плавной нормализации
        data["ID посетителя"] = data["ID посетителя"] / 100000000

        # Преобразуем колонки в массив
        x_data = np.array(data[digit_col].values)
        x_data = x_data.astype("float32")

        # Нормализуем массив
        max_val = x_data.max()
        x_data = x_data / max_val

        # Логируем успешное выполнение функции
        logger.info("Преобразование числовых колонок успешно")

        return x_data
    except Exception as e:
        # Логируем исключение, если произошла ошибка
        logger.error(
            f"Произошла ошибка при преобразовании числовых колонок в DataFrame: {e}"
        )
        raise
