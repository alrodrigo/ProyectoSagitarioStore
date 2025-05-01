from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .models import Perfil

User = get_user_model()

class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    verbose_name_plural = 'Perfiles'

# Extendemos el UserAdmin existente en lugar de crear uno nuevo
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'is_active', 'date_joined']
    search_fields = ['email', 'first_name', 'last_name']
    list_filter = ['is_active', 'is_staff']
    ordering = ['-date_joined']
    inlines = [PerfilInline]

# Des-registramos el UserAdmin por defecto y registramos nuestro CustomUserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'ci', 'telefono', 'ciudad_residencia']
    search_fields = ['usuario__email', 'usuario__first_name', 'usuario__last_name', 'ci', 'telefono']
    list_filter = ['ciudad_residencia']
