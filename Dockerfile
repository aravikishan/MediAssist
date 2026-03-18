FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p instance seed_data

EXPOSE 8011

ENV MEDIASSIST_PORT=8011

CMD ["gunicorn", "--bind", "0.0.0.0:8011", "--workers", "2", "--timeout", "120", "app:create_app()"]
