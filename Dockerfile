FROM python:3.10-alpine

WORKDIR /code/app

RUN apk add --update --no-cache --virtual .tmp-build-deps \
      gcc libc-dev g++

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app  /code/app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]

