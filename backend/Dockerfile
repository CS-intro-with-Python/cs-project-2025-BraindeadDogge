FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# @audit Using one worker for now cause of local storage for urls
# 2 workers give results from random worker's local storage
CMD ["gunicorn", "-b", "0.0.0.0:8000", "-w", "1", "app:create_app()"] 
