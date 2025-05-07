from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('perfil/', views.perfil, name='perfil'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    # Lista de deseos
    path('wishlist/toggle/', views.toggle_lista_deseos, name='toggle_lista_deseos'),
    path('wishlist/', views.mi_lista_deseos, name='mi_lista_deseos'),
    
    # Password reset URLs
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset/confirm/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/complete/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
