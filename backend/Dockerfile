FROM python:3.11-slim
WORKDIR /app

# system deps for psycopg2
RUN apt-get update && apt-get install -y build-essential default-libmysqlclient-dev gcc libpq-dev --no-install-recommends && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app
ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
