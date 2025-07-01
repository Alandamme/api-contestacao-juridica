# Imagem base oficial do Python com menos peso
FROM python:3.13-slim-bookworm

# Define diretório de trabalho
WORKDIR /app

# Evita buffering nos logs (importante no Render)
ENV PYTHONUNBUFFERED=1

# Instala dependências de sistema necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    tcl8.6-dev tk8.6-dev python3-tk \
    libglib2.0-0 libgl1-mesa-glx libxrender1 libsm6 libxext6 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copia as dependências e instala com cache otimizado
COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Copia todo o código-fonte para a imagem final
COPY . .

# Expõe a porta padrão da aplicação Flask
EXPOSE 5000

# Comando de inicialização via Gunicorn (produção)
CMD ["gunicorn", "src.main:app", "--bind", "0.0.0.0:5000"]

