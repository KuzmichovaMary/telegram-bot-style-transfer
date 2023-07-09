# Что это за проект
---

Telegram Bot для перенесения стиля с одной картинки на другую [magents arbitrary style transfer](https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2), а также для стилизации картинки в соответствии с выбранным стилем [fast style transfer](https://github.com/lengstrom/fast-style-transfer).
С помощью бота можно сделать катринку мультяшной с помощью [CartoonGan](https://tfhub.dev/sayakpaul/lite-model/cartoongan/dr/1).

Для пользования ботом перейдите [по ссылке](https://t.me/dls2023_style_bot) и нажмите `/start`.

# Установка

---

## Тестирование и локальный запуск
---

Необходим [питон версии 3.10>=](https://www.python.org/downloads/).

1. Установить `poetry`. ```curl -sSL https://install.python-poetry.org | python3 -
``` для Linux, MacOS и Windows WSL ```(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -``` для Windows PowerShell. (Не забудьте прописать путь до `poetry` в `PATH`)
2. Склонить проект ```git clone https://github.com/KuzmichovaMary/telegram-bot-style-transfer.git```
3. Зайти в папку с проектом ```cd telegram-bot-style-transfer.git```
4. Создать файл `.env` с переменной `TG_BOT_TOKEN` или прописать эту переменную в переменные среды.
5. Запустить ```poetry install --no-root```
6. Запустить ```poetry run python3 app.py```

## Запуск на сервере

---

Для работы необходим установленный докер ([как установить](https://docs.docker.com/engine/install/)) и [питон 3.10>=](https://www.python.org/downloads/).

1. Склонить проект ```git clone https://github.com/KuzmichovaMary/telegram-bot-style-transfer.git```
2. Зайти в папку с проектом ```cd telegram-bot-style-transfer.git```
3. Собрать докер-образ ```docker build -t telegram-bot-style-transfer --build-arg BOT_TOKEN=<YOUR TOKEN> .```
4. Запустить докер-образ ```docker run --name style-transfer -it telegram-bot-style-transfer```


