import os
import re
import shutil
import json
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np
from datetime import datetime
from dataclasses import dataclass
import logging
import pickle as pkl
from typing import List
from fastapi import HTTPException
from pydantic import ValidationError
from sklearn.preprocessing import OneHotEncoder
from models import DataModel, DataOutput
import pandas as pd

from keras.preprocessing.text import Tokenizer
from keras.saving import load_model

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Устанавливаем уровень логирования

# Создаем обработчик для записи в файл
handler = logging.FileHandler("app.log", encoding="utf-8")
handler.setLevel(logging.DEBUG)

# Создаем форматтер для определения формата логов
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)

# Добавляем обработчик к логгеру
logger.addHandler(handler)

# Загрузка предобученной модели.
model = load_model("Materials/model9_21.h5")

# Загрузка токенайзера и энкодеров необходимых для подготовки данных
with open("Materials/token_encoders.pkl", "rb") as f:
    encoders, tokenizer_txt = pkl.load(f)

new_encoders = {key.replace(" ", "_"): value for key, value in encoders.items()}

INPUT_FILES_PATH = "input_data"  # Путь к папке с файлами


def load_data_to_dataframe(project_id: str):
    file_path = os.path.join(INPUT_FILES_PATH, f"{project_id}.json")

    try:
        with open(file_path, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)
        df = pd.DataFrame(data)
        df = clean_text_df(df)
        text_bow = text_to_bow(df)
        ohe_data = ohe_columns(df)
        x_data = digit_cols(df)
        y_pred = model.predict(
            {"input_x1": text_bow, "input_x2": ohe_data, "input_x3": x_data},
            batch_size=text_bow.shape[0],
        )

        df.insert(3, "y_pred", value=np.rint(y_pred))

        # Преобразуем 'call_session' в строковый тип, чтобы избежать проблем с типами данных
        df["call_session"] = df["call_session"].astype(str)

        # Создаем словарь сопоставления по 'call_session' и 'y_pred'
        mapping_dict = dict(zip(df["call_session"], df["y_pred"]))

        data_output_list = []
        for item in data:
            call_session = item.get("call_session", None)
            predict = mapping_dict.get(str(call_session), 0)
            data_output = DataOutput(call_session=call_session, predict=predict)
            data_output_list.append(data_output)

        # Преобразуем список в список словарей
        data_output_dict_list = [
            data_output.model_dump() for data_output in data_output_list
        ]

        # Возвращаем данные в формате JSON
        return data_output_dict_list

    except FileNotFoundError:
        raise Exception(f"Project not found: {project_id}")
    except json.JSONDecodeError:
        raise Exception("Error decoding JSON")
    except Exception as e:
        raise Exception(f"Internal Server Error: {str(e)}")


# Функция очистки входных данных и исправления ключей словаря
def clean_data(data_list: List[dict]) -> List[dict]:
    cleaned_data_list = []
    for data in data_list:
        cleaned_data = {
            k.replace(" ", "_"): remove_braces(str(v)) for k, v in data.items()
        }
        cleaned_data_list.append(cleaned_data)
    return cleaned_data_list


# Перевод длительности звонков из вида 00:00:00 в секунды
def time_to_seconds(time_str):
    if time_str:
        time_obj = datetime.strptime(time_str, "%H:%M:%S")
        return time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second
    return 0


# Функция удаления {}
def remove_braces(value):
    # Удаляем фигурные скобки из значения
    return value.replace("{", "").replace("}", "")


# Функция очистки текста транскрибации от лишних символов и пустых строк
def clean_text(text):
    if text is None:
        return "безответа"

    # Используем регулярное выражение, чтобы оставить только русские буквы и цифры
    cleaned_text = re.sub(r"[^а-яА-Я0-9]", " ", text)

    # Проверяем, не является ли строка пустой после очистки
    if not cleaned_text.strip():
        return "безответа"

    # Удаляем лишние пробелы и приводим к нижнему регистру
    cleaned_text = " ".join(cleaned_text.split()).lower()
    return cleaned_text


def clean_text_df(data: pd.DataFrame):
    data["whisper"] = data["whisper"].apply(clean_text)
    return data


def text_to_bow(data: pd.DataFrame):
    # Получение матрицы BOW для колонки с расшифровками
    txt_list = data["whisper"].tolist()  # Список расшифровок звонков
    text_bow = tokenizer_txt.texts_to_matrix(txt_list)
    return text_bow


def df_to_ohe(df, collist, lst_encoders={}):
    """
    Процедура поочередного преобразования колонок из списка через OneHotEncoder в ОНЕ
    С последующей сборкой в единый массив. Параметры:
    df - датафрейм
    collist - список колонок
    Возвращает собранный массив и список энкодеров
    """
    create_encode = True if len(lst_encoders) == 0 else False
    # print(create_encode)
    list_code = []
    for i in range(len(collist)):
        if create_encode:
            print(
                f"Формирование OneHotEncoder и кодировка колонки {collist[i]}", end=""
            )
            encoder = OneHotEncoder(
                handle_unknown="infrequent_if_exist", sparse_output=False
            )
            encoder.fit(np.array(df[collist[i]].values).reshape(-1, 1))
            lst_encoders[collist[i]] = encoder
            list_code.append(
                encoder.transform(np.array(df[collist[i]].values).reshape(-1, 1))
            )
            print(" - Успешно")
        else:
            # print(f'Кодируется колонка {collist[i]}', end='')
            encoder = lst_encoders[collist[i]]
            list_code.append(
                encoder.transform(np.array(df[collist[i]].values).reshape(-1, 1))
            )
            # print(' - Успешно')

    x_data = np.hstack(list_code)
    return x_data, lst_encoders


def ohe_columns(data: pd.DataFrame, encoders=new_encoders):
    # Получение матрицы ОНЕ
    col_to_ohe = [
        "Статус",
        "Тип",
        "Сайт",
        "Тип_посетителя",
        "Сценарий",
        "Операции",
        "Тип_устройства",
        "Первая_рекламная_кампания",
    ]
    data[col_to_ohe] = data[col_to_ohe].fillna(
        "Нет данных"
    )  # Дозаполним незаполненные данные
    ohe_data, encoders = df_to_ohe(data, col_to_ohe, lst_encoders=encoders)
    ohe_data = ohe_data.astype("float32")
    return ohe_data


def digit_cols(data: pd.DataFrame):
    # Массив из числовых колонок
    digit_col = ["Чистая_длительность_разговора", "Номер_обращения", "ID_посетителя"]
    data[digit_col] = data[digit_col].fillna(0)  # Дозаполнение если есть незаполненные
    data["ID_посетителя"] = (
        data["ID_посетителя"] / 100000000
    )  # Понижение разрядноси колонки для более плавной нормализации
    x_data = np.array(data[digit_col].values)
    x_data = x_data.astype("float32")
    # Нормализация массива
    max_val = x_data.max()
    x_data = x_data / max_val
    return x_data


def main():
    # df = load_data_to_dataframe("1")
    # df = clean_text_df(df)
    # text_bow = text_to_bow(df)

    # new_encoders = {key.replace(" ", "_"): value for key, value in encoders.items()}
    # ohe_data = ohe_columns(df, new_encoders)
    print(load_data_to_dataframe("1"))


if __name__ == "__main__":
    main()
