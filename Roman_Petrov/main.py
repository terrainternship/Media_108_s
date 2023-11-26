import asyncio
import json
import os
from fastapi import BackgroundTasks, FastAPI, HTTPException
import concurrent.futures

from pydantic import ValidationError
from tqdm import tqdm
from transcribe import transcribe_and_update
from typing import List
from models import DataModel, DataOutput
from core import logger, clean_data, load_data_to_dataframe

app = FastAPI()


async def process_data(data: List[dict]):
    json_folder = os.path.join("input_data")
    os.makedirs(json_folder, exist_ok=True)

    for item in data:
        project_id = item.get("ID_проекта", "unknown")

        json_filename = os.path.join(json_folder, f"{project_id}.json")

        try:
            with open(json_filename, "r", encoding="utf-8") as json_file:
                existing_data = json.loads(json_file.read())
        except FileNotFoundError:
            existing_data = []
        except json.JSONDecodeError:
            existing_data = []

        # Создаем экземпляр DataModel из словаря
        data_model_instance = DataModel(**item)

        # Проверяем наличие call_session в существующих данных
        if data_model_instance.call_session not in [
            item.get("call_session") for item in existing_data
        ]:
            try:
                # Добавляем экземпляр DataModel к существующим данным
                existing_data.append(data_model_instance.model_dump())

                with open(json_filename, "w", encoding="utf-8") as json_file:
                    json.dump(
                        existing_data,
                        json_file,
                        ensure_ascii=False,
                    )
                    json_file.write("\n")
            except ValidationError as e:
                error_message = f"Validation error for data: {item}"
                logger.error(error_message)
                print(error_message)


# async def transcribe_and_update_async(json_paths):
#     max_workers = 1
#     # Используем ProcessPoolExecutor для запуска transcribe_and_update_async в отдельном процессе
#     with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
#         tasks = [
#             executor.submit(transcribe_and_update, json_path)
#             for json_path in json_paths
#         ]

#         # Ожидаем завершения каждой задачи
#         for future in tqdm(
#             concurrent.futures.as_completed(tasks),
#             total=len(tasks),
#             desc="Processing",
#         ):
#             print(future)
#             try:
#                 future.result()
#             except Exception as e:
#                 logger.error(f"An error occurred: {e}")
#                 raise HTTPException(
#                     status_code=400, detail=f"Error processing data: {e}"
#                 )


@app.post("/your_endpoint")
async def your_endpoint(data_list: List[dict]):
    json_paths = []
    inp_data = "input_data"
    try:
        cleaned_data_list = clean_data(data_list)

        await process_data(cleaned_data_list)

        for i in os.listdir(inp_data):
            json_path = os.path.join(inp_data, i)
            json_paths.append(json_path)

        max_workers = 1
        # Используем ProcessPoolExecutor для запуска transcribe_and_update_async в отдельном процессе
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=max_workers
        ) as executor:
            tasks = [
                executor.submit(transcribe_and_update, json_path)
                for json_path in json_paths
            ]

            # Ожидаем завершения каждой задачи
            for future in tqdm(
                concurrent.futures.as_completed(tasks),
                total=len(tasks),
                desc="Processing",
            ):
                print(future)
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"An error occurred: {e}")
                    raise HTTPException(
                        status_code=400, detail=f"Error processing data: {e}"
                    )

        # # Добавляем задачу в фоновый процесс
        # BackgroundTasks.add_task(transcribe_and_update_async, json_paths)

        return "Данные приняты корректно"
    except Exception as e:
        logger.error(f"An error occurred: {e}")

        raise HTTPException(status_code=400, detail=f"Error processing data: {e}")


@app.get("/project/{project_id}", response_model=List[DataOutput])
async def read_project(project_id: str):
    try:
        result = load_data_to_dataframe(project_id)

        return result
    except HTTPException as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Internal Server Error: {str(e)}"}


async def mains():
    # result = load_data_to_dataframe("1")
    # print(result)
    json_paths = []
    inp_data = "input_data"
    for i in os.listdir(inp_data):
        json_path = os.path.join(inp_data, i)
        json_paths.append(json_path)
    # # Загрузка данных из файла JSON
    # with open("df.json", "r", encoding="utf-8") as json_file:
    #     data = json.load(json_file)
    # cleaned_data_list = clean_data(data)
    # await process_data(cleaned_data_list)

    # # Ограничиваем количество одновременно работающих процессов
    max_workers = 1

    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        tasks = [
            executor.submit(transcribe_and_update, json_path)
            for json_path in json_paths
        ]

        # Ожидаем завершения каждой задачи
        for future in tqdm(
            concurrent.futures.as_completed(tasks), total=len(tasks), desc="Processing"
        ):
            try:
                future.result()
            except Exception as e:
                logger.error(f"An error occurred: {e}")
                raise HTTPException(
                    status_code=400, detail=f"Error processing data: {e}"
                )


if __name__ == "__main__":
    asyncio.run(mains())
