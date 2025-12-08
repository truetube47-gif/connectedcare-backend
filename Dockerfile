FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY drugs.xlsx .
COPY import_drugs.py .
COPY app ./app
COPY auth ./auth
COPY firebase_admin.py .

# Railway injects PORT dynamically
ENV PORT=8000

EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT --log-level debug || sleep 3600"]

