#!/bin/bash

# Verificar si se necesita crear un entorno virtual
if [ ! -d "venv" ]; then
    echo "Creando entorno virtual..."
    python -m venv venv
    echo "Entorno virtual creado."
fi

# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno para WhatsApp
echo "# Variables de entorno para la API de WhatsApp" > .env
echo "WHATSAPP_PHONE_NUMBER_ID=tu_phone_number_id" >> .env
echo "WHATSAPP_ACCESS_TOKEN=tu_access_token" >> .env

echo "Configuración completada. Para activar el entorno virtual usa: source venv/bin/activate"
echo "IMPORTANTE: Edita el archivo .env con tus credenciales reales de WhatsApp Business API"