FROM python:3.13-slim-bookworm

WORKDIR /app

# ✅ Instala dependências do sistema para PyMuPDF (fitz) e libs gráficas
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
    libglib2.0-0 \
    libgl1-mesa-glx \
    libxrender1 \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala dependências do projeto
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código-fonte da aplicação
COPY . .

# Exponha a porta (Render usa a env PORT)
EXPOSE 5000

# Comando de inicialização da API com gunicorn
CMD ["gunicorn", "src.main:app", "--bind", "0.0.0.0:5000"]


