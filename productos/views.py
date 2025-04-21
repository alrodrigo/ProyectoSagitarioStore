from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Product, Category
from unidecode import unidecode
from django.views.generic import ListView, DetailView

def home(request):
    products = Product.objects.all()
    return render(request, 'productos/home.html', {'products': products})

def search(request):
    query = request.GET.get('q', '')
    if query:
        productos = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct()
    else:
        productos = Product.objects.none()
    
    paginator = Paginator(productos, 12)
    page = request.GET.get('page')
    productos = paginator.get_page(page)
    
    return render(request, 'productos/search.html', {
        'query': query,
        'productos': productos,
    })

def anime(request):
    categoria_anime = get_object_or_404(Category, name='Anime')
    productos_list = Product.objects.filter(category=categoria_anime)
    paginator = Paginator(productos_list, 12)
    
    page = request.GET.get('page')
    productos = paginator.get_page(page)
    
    return render(request, 'productos/categorias/anime.html', {
        'categoria': categoria_anime,
        'productos': productos,
    })

def superheroes(request):
    categoria_super = get_object_or_404(Category, name='Superhéroes')
    productos_list = Product.objects.filter(category=categoria_super)
    paginator = Paginator(productos_list, 12)
    
    page = request.GET.get('page')
    productos = paginator.get_page(page)
    
    return render(request, 'productos/categorias/superheroes.html', {
        'categoria': categoria_super,
        'productos': productos,
    })

def producto(request, id):
    producto = get_object_or_404(Product, id=id)
    productos_relacionados = Product.objects.filter(
        category=producto.category
    ).exclude(id=producto.id)[:3]
    
    return render(request, 'productos/detalle/producto.html', {
        'producto': producto,
        'productos_relacionados': productos_relacionados,
    })

def category_view(request, category_name):
    # Normalizar el nombre de la categoría (quitar tildes y convertir a minúsculas)
    normalized_name = unidecode(category_name.lower())
    
    # Buscar la categoría ignorando mayúsculas/minúsculas y tildes
    categories = Category.objects.all()
    category = None
    for cat in categories:
        if unidecode(cat.name.lower()) == normalized_name:
            category = cat
            break
    
    if not category:
        from django.http import Http404
        raise Http404("No se encontró la categoría")
    
    products_list = Product.objects.filter(category=category)
    
    # Add pagination
    paginator = Paginator(products_list, 12)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    
    return render(request, 'productos/categorias/category.html', {
        'category_name': category.name,
        'category': category,
        'products': products
    })

def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    related_products = Product.objects.filter(category=product.category).exclude(id=id)[:3]
    return render(request, 'productos/detalle/producto.html', {
        'producto': product,
        'productos_relacionados': related_products
    })

class CategoryView(ListView):
    model = Product
    template_name = 'productos/categorias/category.html'  # Actualizado a la nueva estructura
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        category_slug = self.kwargs.get('category_slug')
        category = get_object_or_404(Category, slug=category_slug)
        
        # Handle sorting
        sort_param = self.request.GET.get('sort', 'popular')
        # Removed filtering by non-existent 'is_active' field
        products = Product.objects.filter(category=category)
        
        if sort_param == 'price-low':
            products = products.order_by('price')
        elif sort_param == 'price-high':
            products = products.order_by('-price')
        elif sort_param == 'newest':
            products = products.order_by('-created_at')
        # Removed ordering by non-existent 'sold_count' and 'rating' fields for 'popular'
        # Defaulting to newest for now if 'popular' is selected or no sort is specified
        else: # Default: popular (or newest as fallback)
             products = products.order_by('-created_at')
            
        return products
    
    def get_template_names(self):
        category_slug = self.kwargs.get('category_slug')
        # Actualizado a la nueva estructura de directorios
        specific_template = f'productos/categorias/{category_slug}.html'
        return [specific_template, 'productos/categorias/category.html']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs.get('category_slug')
        category = get_object_or_404(Category, slug=category_slug)
        context['category'] = category
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = 'productos/detalle/producto.html'  # Actualizado a la nueva estructura
    context_object_name = 'product'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        
        # Add related products
        # Removed filtering by non-existent 'is_active' field
        related_products = Product.objects.filter(
            category=product.category
        ).exclude(id=product.id)[:4]
        
        # Calculate discount percentage if applicable
        if product.original_price and product.original_price > product.price:
            discount = (product.original_price - product.price) / product.original_price * 100
            product.discount_percent = int(discount)
        
        # Add rating with ceiling for half-stars
        import math
        product.rating_ceil = math.ceil(product.rating)
        
        context['related_products'] = related_products
        return context
