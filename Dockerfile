# Use official Python image
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose Flask default port
EXPOSE 5000

CMD ["python", "app.py"] 