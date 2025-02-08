# Usar Python 3.9 como base
FROM python:3.9

# Establecer el directorio de trabajo en /app
WORKDIR /app

# Copiar los archivos del código al contenedor
COPY . .

# Actualizar pip y instalar las dependencias desde requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Definir variables de entorno dentro del contenedor (para evitar errores)
ENV BINANCE_API_KEY="SB9riIpm8RMgw36NDvHVoHPWDt41DU16NJbcLw7EdOurws15jdMJLSxQeBoYgtbf"
ENV BINANCE_API_SECRET="HDDuvOW6Njy17QpwzuYjMnV8i1ujS7RCUM7BzrG2lBDeOIkFEwk0HoPqtWyILajT"

# Definir la variable de entorno del puerto
ENV PORT=8080

# Exponer el puerto 8080 para Flask
EXPOSE 8080

# Comando para ejecutar el bot
CMD ["python", "botxrp.py"]


