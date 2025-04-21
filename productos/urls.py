from django.urls import path
from . import views

app_name = 'productos'

urlpatterns = [
    path('', views.home, name='home'),
    # Use CategoryView and capture slug instead of name
    path('categoria/<slug:category_slug>/', views.CategoryView.as_view(), name='categoria'),
    path('producto/<int:id>/', views.product_detail, name='producto'),
]

