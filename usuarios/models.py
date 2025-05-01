from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()

class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    ci = models.CharField('Cédula de Identidad', max_length=20, blank=True)
    telefono = models.CharField('Número de teléfono', max_length=20, blank=True)
    ciudad_residencia = models.CharField('Ciudad de residencia', max_length=100, blank=True)
    direccion = models.TextField('Dirección completa', blank=True)
    
    def __str__(self):
        return f"Perfil de {self.usuario.get_full_name() or self.usuario.email}"

# Señal para crear automáticamente un perfil cuando se crea un usuario
@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(usuario=instance)

# Señal para guardar el perfil cuando se guarda un usuario
@receiver(post_save, sender=User)
def guardar_perfil_usuario(sender, instance, **kwargs):
    try:
        instance.perfil.save()
    except Perfil.DoesNotExist:
        Perfil.objects.create(usuario=instance)
