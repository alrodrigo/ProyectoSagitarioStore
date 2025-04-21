#!/bin/bash

echo "Configurando el proyecto Sagitario Store..."

# Crear las carpetas necesarias
mkdir -p templates/componentes
mkdir -p templates/usuarios
mkdir -p templates/pedidos
mkdir -p static/css
mkdir -p static/js
mkdir -p static/images
mkdir -p media/productos

# Recolectar archivos estáticos
echo "Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

# Realizar migraciones si es necesario
echo "Aplicando migraciones..."
python manage.py makemigrations
python manage.py migrate

echo "¡Configuración completada!"
echo "Para iniciar el servidor, ejecuta: python manage.py runserver"
