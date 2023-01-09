FROM python:3.11.1-slim

WORKDIR /app/

RUN apt-get update
RUN apt-get install build-essential -y
RUN apt-get install pkg-config -y --no-install-recommends

COPY pyproject.toml requirements.txt  /app/

RUN pip install -r requirements.txt

COPY pyrelay /app/pyrelay
ENV PYTHONPATH=/app
