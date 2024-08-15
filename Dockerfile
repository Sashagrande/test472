FROM python:3.12

ENV PYTHONUNBUFFERED=1
ENV POETRY_VIRTUALENVS_CREATE=false

COPY . /app
COPY ./src /app/src
ENV PYTHONPATH /app

WORKDIR /app

RUN python -m pip install poetry==1.4.2 wheel==0.38.4 && \
    poetry install --no-interaction --no-ansi