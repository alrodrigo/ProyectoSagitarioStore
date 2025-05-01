#!/bin/bash

echo "================================================"
echo "      Configurando Sagitario Store v1.0          "
echo "================================================"

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "Python 3 no está instalado. Por favor instálalo antes de continuar."
    exit 1
fi

# Verificar entorno virtual
if [ ! -d "venv" ]; then
    echo "Creando entorno virtual..."
    python3 -m venv venv
    echo "✅ Entorno virtual creado."
else
    echo "✅ Entorno virtual ya existe."
fi

# Activar entorno virtual
echo "Activando entorno virtual..."
source venv/bin/activate

# Actualizar pip
echo "Actualizando pip..."
pip install --upgrade pip

# Verificar e instalar dependencias
echo "Instalando dependencias requeridas..."
pip install -r requirements.txt
echo "✅ Dependencias instaladas."

# Configurar archivo .env si no existe
if [ ! -f ".env" ]; then
    echo "Creando archivo .env con configuración básica..."
    cat > .env << EOL
# Configuración del entorno
DEBUG=True
SECRET_KEY=django-insecure-z2wl-91@un28()=s7d&j9$k5_+prlb9vy0wmrpz3+b*=oxe2i+

# Configuración de la base de datos (opcional para bases de datos externas)
# DATABASE_URL=sqlite:///db.sqlite3
# DATABASE_URL=postgres://usuario:contraseña@localhost:5432/sagitariostore

# Configuración de WhatsApp Business API
WHATSAPP_PHONE_NUMBER_ID=
WHATSAPP_ACCESS_TOKEN=
WHATSAPP_AUTO_SEND=False

# Configuración de email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=Sagitario Store <noreply@sagitariostore.com>
EOL
    echo "✅ Archivo .env creado. Recuerda completar las credenciales."
else
    echo "✅ Archivo .env ya existe."
fi

# Crear estructura de directorios si no existe
echo "Creando estructura de directorios necesaria..."
mkdir -p templates/{componentes,usuarios,pedidos,productos,carrito,admin}
mkdir -p static/{css,js,images,icons}
mkdir -p media/{products,categories,comprobantes,pagos/qr,pagos/qr_predefinidos}

# Recolectar archivos estáticos
echo "Recolectando archivos estáticos..."
python manage.py collectstatic --noinput
echo "✅ Archivos estáticos recolectados."

# Realizar migraciones
echo "Aplicando migraciones..."
python manage.py makemigrations
python manage.py migrate
echo "✅ Base de datos actualizada."

# Preguntar si se desea crear un superusuario
read -p "¿Deseas crear un superusuario para el panel de administración? (s/n): " crear_admin
if [[ $crear_admin == "s" || $crear_admin == "S" ]]; then
    python manage.py createsuperuser
    echo "✅ Superusuario creado."
fi

# Preguntar si se desea configurar WhatsApp
read -p "¿Deseas configurar la API de WhatsApp ahora? (s/n): " config_whatsapp
if [[ $config_whatsapp == "s" || $config_whatsapp == "S" ]]; then
    read -p "Ingresa el WHATSAPP_PHONE_NUMBER_ID: " phone_id
    read -p "Ingresa el WHATSAPP_ACCESS_TOKEN: " access_token
    read -p "¿Habilitar envío automático de mensajes? (s/n): " auto_send
    
    # Actualizar el archivo .env
    sed -i "s/^WHATSAPP_PHONE_NUMBER_ID=.*/WHATSAPP_PHONE_NUMBER_ID=$phone_id/" .env
    sed -i "s/^WHATSAPP_ACCESS_TOKEN=.*/WHATSAPP_ACCESS_TOKEN=$access_token/" .env
    
    if [[ $auto_send == "s" || $auto_send == "S" ]]; then
        sed -i "s/^WHATSAPP_AUTO_SEND=.*/WHATSAPP_AUTO_SEND=True/" .env
    else
        sed -i "s/^WHATSAPP_AUTO_SEND=.*/WHATSAPP_AUTO_SEND=False/" .env
    fi
    
    echo "✅ Configuración de WhatsApp actualizada."
fi

# Comprobar si django-environ está instalado
if ! pip show django-environ > /dev/null; then
    echo "Instalando django-environ para manejar variables de entorno..."
    pip install django-environ
    pip freeze > requirements.txt
    echo "✅ django-environ instalado y requirements.txt actualizado."
fi

# Verificar si tenemos fixture de datos iniciales y preguntar si se desea cargarlos
if [ -d "fixtures" ]; then
    read -p "¿Deseas cargar los datos iniciales de ejemplo? (s/n): " cargar_datos
    if [[ $cargar_datos == "s" || $cargar_datos == "S" ]]; then
        echo "Cargando datos iniciales..."
        python manage.py loaddata fixtures/*.json
        echo "✅ Datos iniciales cargados."
    fi
fi

echo ""
echo "================================================"
echo "     ¡Configuración completada con éxito!       "
echo "================================================"
echo ""
echo "Para iniciar el servidor de desarrollo, ejecuta:"
echo "source venv/bin/activate && python manage.py runserver"
echo ""
echo "Para acceder al panel de administración:"
echo "http://127.0.0.1:8000/admin/"
echo ""
echo "¡Gracias por usar Sagitario Store!"
