#Imagen base
FROM python:3.12-slim

#Directorio de trabajo
WORKDIR /app

#Copiar dependencias e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#Copiar codigo
COPY . .

#Puerto
EXPOSE 8000

#Comando por defecto (API)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]