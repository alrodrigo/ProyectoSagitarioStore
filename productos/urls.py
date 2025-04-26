from django.urls import path
from . import views

app_name = 'productos'

urlpatterns = [
    path('', views.home, name='home'),
    # Ruta para lista de todos los productos
    path('productos/', views.ProductListView.as_view(), name='lista_productos'),
    # Ruta para categorías principales
    path('categoria/<slug:category_slug>/', views.CategoryView.as_view(), name='categoria'),
    # Ruta para subcategorías
    path('categoria/<slug:category_slug>/<slug:subcategory_slug>/', views.SubCategoryView.as_view(), name='subcategoria'),
    # Ruta para pruebas de acceso directo a subcategorías (por ID)
    path('subcategoria-por-id/<int:subcategory_id>/', views.subcategory_by_id, name='subcategoria_por_id'),
    # Ruta para productos
    path('producto/<int:id>/', views.ProductDetailView.as_view(), name='producto'),
]

