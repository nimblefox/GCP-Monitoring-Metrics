FROM python:3.10-slim

ENV PYTHONBUFFERED True
ENV APP_HOME /app

WORKDIR ${APP_HOME}

COPY ./src/ ./

RUN pip install -r requirements.txt

CMD ["python", "main.py"]