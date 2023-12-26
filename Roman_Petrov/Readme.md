Чтобы поднять проект, необходимо:

- скачать файлы с репозитория
- скачать и добавить потом в скачанные на диск файлы в папку app/Materials с гугл диска [энкодер/токенайзер и Keras модель](https://drive.google.com/drive/folders/1PXvPCz712B7OafGqrr-Q3vlEgX_VWl-6?usp=sharing)
Либо сразу скачать все файлы с [гугл диска](https://drive.google.com/drive/folders/12P89qrj64omgC7jzlTqg5GRbgqWH91p-?usp=sharing) разом
[Тестовые аудиозаписи](https://drive.google.com/drive/folders/1WdprQ8kJxUbwHWN8xd_JpD13A9ZxY4fE?usp=sharing) скачать и разместить у себя на диске. В файле docker-compose заменить volumes на ваше расположение папки с аудиозаписями.

![image](https://github.com/terrainternship/Media_108_s/assets/17458625/18c434a7-5286-454f-b870-a557627102f1)

После этого можно выполнить команды:

```
docker-compose build
docker-compose up
```
После запуска всех контейнеров:
- Api **fastapi_app** будет доступен по адресу **"localhost:9999"***
- Api **whisper** будет доступен по адресу "localhost:9000"
- Api **flower** будет доступен по адресу "localhost:8888"

В корневой папке в файле tests.json расположены тестовые данные, которые будут приходить от заказчика по Api в FastApi приложение на endpoint "/create_records/". Данные из tests.json соответствую тестовым аудиозаписям.

Сервис whisper использует модель=base, можно сменить на другую модель (tiny, base, small, medium, large) в файле docker-compose
![image](https://github.com/terrainternship/Media_108_s/assets/17458625/e45a0edc-08f7-44eb-8fd0-7e30f112e67b)

Сервис celery-beat запускает каждую минуту 2 задачи:
1. Проверка новых записей для транскрипции
  - Запуск транскрипции
  - Запись транскрипции в запись
  - Обновление статуса do_transcription у записи
2. Проверка новых записей, доступных для предикта
 - Проверяет есть ли новые записи для предикта
 - Делает предикт и обновляет запись в predict_model1

