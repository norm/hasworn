FROM python:3.9.6-alpine3.14

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /app

# psycopg support
RUN    apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev

# python libs
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

ENTRYPOINT ["/app/wait.sh"]
