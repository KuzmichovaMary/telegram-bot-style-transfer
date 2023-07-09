FROM ubuntu:22.04

COPY . ./

RUN curl -sSL https://install.python-poetry.org | python3 -

ARG BOT_TOKEN
ENV TG_BOT_TOKEN=$BOT_TOKEN

RUN poetry install

CMD ["poetry", "run", "python3", "bot.py"]
