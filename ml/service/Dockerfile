FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ml /app/ml
WORKDIR /app/ml/service

COPY ml/service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create package markers
RUN touch /app/ml/__init__.py /app/ml/models/__init__.py /app/ml/service/__init__.py

EXPOSE 7860

HEALTHCHECK CMD curl --fail http://localhost:7860/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
