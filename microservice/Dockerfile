FROM python:3.10.11-alpine

ENV PYTHONUNBUFFERED 1

RUN mkdir /blog_microservice

WORKDIR /blog_microservice

COPY requirements.txt .

RUN apk add --no-cache gcc musl-dev && \
    pip install -r requirements.txt && \
    apk del gcc musl-dev

COPY . .

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]