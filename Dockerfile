FROM python:3.13-slim-bookworm

WORKDIR /app

# Instala as ferramentas de build e libs para PyMuPDF e arquivos gráficos
RUN apt-get update && apt-get install -y \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    tcl8.6-dev \
    tk8.6-dev \
    python3-tk \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala dependências
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copia a aplicação inteira
COPY . .

# Exponha a porta 5000 (Render usa a variável de ambiente PORT)
EXPOSE 5000

# Use Gunicorn para rodar o app Flask via src.main:app
CMD ["gunicorn", "src.main:app"]

