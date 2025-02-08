# Usa una imagen base de Python
FROM python:3.9

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos del proyecto al contenedor
COPY . .

# Instala dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto que usará Cloud Run
ENV PORT=8080
EXPOSE 8080

# Comando para ejecutar el bot
CMD ["python", "botxrp.py"]


