FROM python:3.11-slim

# Install system dependencies for prophet and pandas
RUN apt-get update && apt-get install -y --no-install-recommends gcc g++ make && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the entire ml directory
COPY ml /app/ml

# Work in the service directory
WORKDIR /app/ml/service

# Install dependencies
COPY ml/service/requirements.txt .
RUN pip install --no-cache-dir --only-binary :all: -r requirements.txt

EXPOSE 7860

# Health check
HEALTHCHECK CMD curl --fail http://localhost:7860/health || exit 1

# Run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
