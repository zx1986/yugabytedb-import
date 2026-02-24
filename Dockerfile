FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir psycopg2-yugabytedb-binary>=2.9.9

COPY src/ ./src/

ENTRYPOINT ["python", "src/main.py"]
