import pandas as pd

csv_file = "Materials/df_no_teg.csv"

df = pd.read_csv(csv_file)


# Функция для добавления префикса
def add_prefix(filename):
    return f"Materials/Audio/{filename}"


# Применяем функцию ко всем значениям столбца 'Имя файла'
df["Имя файла"] = df["Имя файла"].apply(add_prefix)
# df["whisper"] = ""
print(df["Имя файла"].unique())


target_values = [
    "Materials/Audio/2023-08-15_10-39-04.246310_from_74955720037_to_00288_session_3161495667_talk.mp3",
    "Materials/Audio/2023-10-04_19-47-06.171534_from_79624005760_to_0111652_session_3264304568_talk.mp3",
    "Materials/Audio/2023-10-05_10-24-51.279862_from_79235257654_to_74959339902_session_3277407497_talk.mp3",
    "Materials/Audio/2023-09-16_18-26-25.054422_from_79916419068_to_0188880_session_3235607367_talk.mp3",
    "Materials/Audio/2023-10-05_09-45-26.114404_from_79154168876_to_0188880_session_3270371969_talk.mp3",
    "Materials/Audio/2023-10-04_10-21-52.432435_from_74950210291_to_0150111_session_3274981007_talk.mp3",
    "Materials/Audio/2023-10-04_13-02-32.947477_from_79652648599_to_0253201_session_3253266390_talk.mp3",
    "Materials/Audio/2023-09-18_12-31-27.901544_from_79099465930_to_00288_session_3230778649_talk.mp3",
    "Materials/Audio/2023-09-18_12-54-18.603506_from_79160620083_to_00288_session_3220199190_talk.mp3",
]

# Предположим, что ваш DataFrame называется df
# Создадим словарь с соответствиями "Name" и "ID проекта"
project_mapping = {"Павелецкая сити": 3, "Примавера": 2, "Headliner": 1}

# Добавим новый столбец "ID проекта" на основе столбца "Name"
df["ID проекта"] = df["Name"].map(project_mapping)
# Перемешиваем записи
shuffled_df = df.sample(frac=1).reset_index(drop=True)

# Сохраняем в JSON
shuffled_df.to_json("data_shuffled.json", orient="records", force_ascii=False)

cols_to_json = [
    "ID проекта",
    "Name",
    "Имя файла",
    "whisper",
    "Статус",
    "Тип",
    "Сайт",
    "Тип посетителя",
    "Сценарий",
    "Операции",
    "Тип устройства",
    "Первая рекламная кампания",
    "Чистая длительность разговора",
    "Номер обращения",
    "ID посетителя",
]
new_df = df[cols_to_json]
# Преобразовываем новый датасет в JSON
json_df = new_df.to_json("dataf.json", orient="records", force_ascii=False)
selected_rows = new_df[new_df["Имя файла"].isin(target_values)]
print(selected_rows)
json_data = selected_rows.to_json("df.json", orient="records", force_ascii=False)

# print(json_data)
