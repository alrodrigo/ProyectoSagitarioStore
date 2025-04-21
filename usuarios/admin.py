from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

User = get_user_model()

# Extendemos el UserAdmin existente en lugar de crear uno nuevo
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'is_active', 'date_joined']
    search_fields = ['email', 'first_name', 'last_name']
    list_filter = ['is_active', 'is_staff']
    ordering = ['-date_joined']

# Des-registramos el UserAdmin por defecto y registramos nuestro CustomUserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
