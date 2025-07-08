# Imagem base leve com Python 3.10 (mais estável que 3.13 no Render Free)
FROM python:3.10-slim-bookworm

WORKDIR /app
ENV PYTHONUNBUFFERED=1

# Instala apenas o necessário para lxml + docxtpl
RUN apt-get update && apt-get install -y \
    build-essential \
    libxml2-dev \
    libxslt1-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências Python
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copia o código
COPY . .

EXPOSE 5000

# Usa apenas 1 worker e timeout ideal p/ Render Free
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5000", "-t", "180", "src.main:app"]



