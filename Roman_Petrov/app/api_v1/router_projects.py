import json
from fastapi import APIRouter, HTTPException, status
from app.api_v1 import crud
from app.core.config import settings
from app.core.utils import logger

router = APIRouter(tags=["Projects"])


@router.post("/projects_id_name")
async def post_projects_id_names(id_names: dict[str, str]) -> dict[str, str]:
    try:
        logger.info("Записываем новые проекты ID names")

        # Вызываем функцию из crud для обработки данных
        data = await crud.post_projects(id_names)

        logger.info("Проекты ID names успешно записаны")

        return data
    except Exception as e:
        # Логируем исключение, если произошла ошибка
        logger.error(f"Произошла ошибка при записи проектов ID names: {e}")

        # Выбрасываем HTTP исключение с кодом 500 и деталями об ошибке
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/projects_id_name")
async def get_projects_id_names() -> dict[str, str]:
    try:
        logger.info("Получаем проекты ID names")

        # Получаем имя файла из настроек
        json_file = settings.json_projects_id_name.split("/")[-1]

        # Вызываем функцию из crud для получения данных
        data = await crud.get_projects_all()

        # Логируем успешное выполнение эндпоинта
        logger.info("Проекты ID names успешно получены")

        return data
    except FileNotFoundError:
        # Логируем ошибку, если файл не найден
        logger.error(f"Файл {settings.json_projects_id_name} не найден")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )
    except json.JSONDecodeError:
        # Логируем ошибку декодирования JSON
        logger.error(f"Error decoding JSON data or JSON {json_file} is empty")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error decoding JSON data or JSON {json_file} is empty",
        )
    except ValueError as ve:
        # Логируем ошибку значения (например, пустой JSON)
        logger.error(f"{json_file} is empty: {ve}")
        raise ValueError(f"{json_file} is empty")
