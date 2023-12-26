import numpy as np
import pandas as pd
from app.core.shemas import RecordBase
from app.core.utils import (
    clean_text_df,
    digit_cols,
    get_record_to_df_data,
    ohe_columns,
    text_to_bow,
    logger,
)
from keras.saving import load_model


def get_predict_model_1(records: list[RecordBase]):
    try:
        logger.info("Выполнение get_predict_model_1")
        records_as_dict = [record.to_dict() for record in records]
        df_data = get_record_to_df_data(records_as_dict)
        df = pd.DataFrame(df_data)
        df = clean_text_df(df)
        text_bow = text_to_bow(df)
        ohe_data = ohe_columns(df)
        x_data = digit_cols(df)
        # Загрузка предобученной модели.
        model = load_model("app/Materials/model9_21.h5")
        y_pred = model.predict(
            {"input_x1": text_bow, "input_x2": ohe_data, "input_x3": x_data},
            batch_size=text_bow.shape[0],
        )
        df.insert(3, "y_pred", value=np.rint(y_pred))
        # Получите измененные данные из DataFrame в виде словаря
        modified_data = df[["Идентификатор сессии звонка", "y_pred"]].to_dict(
            orient="records"
        )
        logger.info("get_predict_model_1 успешно выполнено")
        return modified_data
    except Exception as e:
        # Логируем исключение, если оно произошло
        logger.error(f"Произошла ошибка в get_predict_model_1: {e}")
        raise
