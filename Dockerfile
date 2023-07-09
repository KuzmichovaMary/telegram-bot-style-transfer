FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
curl
RUN curl -sSL https://install.python-poetry.org | python -

WORKDIR /dls-project/

ADD poetry.lock pyproject.toml ./

ENV PATH="/root/.local/bin:$PATH"
ENV PYTHONPATH="/dls-project/"

RUN poetry config virtualenvs.create false
RUN export JOBLIB_START_METHOD="spawn"
RUN poetry install --no-root
RUN poetry show

COPY . .


ARG BOT_TOKEN
ENV TG_BOT_TOKEN=$BOT_TOKEN

CMD ["poetry", "run", "python3", "app.py"]