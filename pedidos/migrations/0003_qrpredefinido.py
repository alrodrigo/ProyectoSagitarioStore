# Generated by Django 5.2 on 2025-04-23 16:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pedidos', '0002_pago'),
    ]

    operations = [
        migrations.CreateModel(
            name='QRPredefinido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(help_text="Un nombre descriptivo para identificar este QR (ej: 'QR Banco BCP')", max_length=100)),
                ('imagen', models.ImageField(upload_to='pagos/qr_predefinidos/', verbose_name='Imagen del código QR')),
                ('instrucciones', models.TextField(help_text='Instrucciones que se mostrarán al usuario para realizar el pago con este QR')),
                ('banco', models.CharField(help_text='Nombre del banco o entidad asociada al QR', max_length=100)),
                ('cuenta', models.CharField(blank=True, help_text='Número de cuenta asociada (opcional)', max_length=100, null=True)),
                ('titular', models.CharField(help_text='Nombre del titular de la cuenta', max_length=150)),
                ('activo', models.BooleanField(default=True, help_text='Desmarcar para deshabilitar este QR sin eliminarlo')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'QR Predefinido',
                'verbose_name_plural': 'QRs Predefinidos',
                'ordering': ['nombre'],
            },
        ),
    ]
