FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/

RUN pip install -r requirements.txt

COPY . /app/

EXPOSE 8000


CMD ["sh", "-c", "python manage.py makemigrations && python manage.py migrate && gunicorn --bind 0.0.0.0:8000 core.wsgi:application"]
