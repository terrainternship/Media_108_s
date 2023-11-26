import whisper
import json
from tqdm import tqdm
from core import logger


def transcribe_and_update(json_filepath, model="medium"):
    # Загрузка модели
    model = whisper.load_model(model)
    options = dict(language="Russian", beam_size=5, best_of=5, fp16=False)
    transcribe_options = dict(task="transcribe", **options)

    # Загрузка данных из JSON-файла
    with open(json_filepath, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)

    # Проведение транскрипции для каждой записи
    for item in tqdm(data):
        if isinstance(item, dict):
            audio_path = item.get("Имя_файла", "")
            # print("Audio Path:", audio_path)
            if audio_path:
                if len(item["whisper"]) == 0:
                    try:
                        # Попытка выполнить транскрипцию
                        result = model.transcribe(audio_path, **transcribe_options)
                        transcription_text = result.get("text", "")
                        item["whisper"] = transcription_text
                    except Exception as transcribe_error:
                        logger.error(f"Transcription error: {transcribe_error}")

    # Обновление данных в JSON-файле
    with open(json_filepath, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False)


def main():
    # Example usage:
    json_filepath = "input_data/2023-11-26/2/2.json"
    transcribe_and_update(json_filepath)


if __name__ == "__main__":
    main()
