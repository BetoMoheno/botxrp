# Usar Python 3.9 como base
FROM python:3.9

# Establecer el directorio de trabajo en /app
WORKDIR /app

# Copiar los archivos del código al contenedor
COPY . .

# Instalar las dependencias desde requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Definir la variable de entorno del puerto
ENV PORT=8080

# Exponer el puerto 8080 para Flask
EXPOSE 8080

# Comando para ejecutar el bot
CMD ["python", "botxrp.py"]


