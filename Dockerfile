FROM python:3.10-slim

ENV PYTHONBUFFERED True
ENV APP_HOME /app
ENV PORT 8080

WORKDIR ${APP_HOME}

COPY ./src/ ./

RUN pip install -r requirements.txt

EXPOSE ${PORT}
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app