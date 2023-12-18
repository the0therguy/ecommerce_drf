FROM python:3.10 AS base
ENV PYTHONBUFFERED=1
WORKDIR /app

COPY requirments.txt requirments.txt
RUN pip install --no-cache-dir -r requirments.txt
COPY . .
EXPOSE 8000
CMD ["python", "manage.py", "makemigrations"]
CMD ["python", "manage.py", "migrate"]
CMD ["python", "manage.py", "collectstatic"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
