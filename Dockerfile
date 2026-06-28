FROM python:3.14-slim

RUN groupadd -r bot && useradd -r -g bot makeroom

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

USER makeroom

CMD ["python3", "main.py"]