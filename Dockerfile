FROM python:3.13-slim-bookworm

WORKDIR /app

# Instala as ferramentas de build C/C++
RUN apt-get update && apt-get install -y build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "src/main.py"]
