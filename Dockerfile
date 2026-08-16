FROM python:3.11-slim

WORKDIR /app

# Instala dependências de sistema para OpenCV e áudio
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copia arquivos de requisitos e instala dependências
COPY backend/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia código do projeto
COPY . .

# Expõe porta
EXPOSE 8000

# Executa servidor FastAPI
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
