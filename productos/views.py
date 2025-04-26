from django.views.generic import ListView, DetailView
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Product, Category

def categories_processor(request):
    """Context processor para añadir categorías y subcategorías a todas las plantillas"""
    main_categories = Category.objects.filter(parent=None).prefetch_related('subcategories')
    categories_dict = {}
    for category in main_categories:
        subcategories = list(category.subcategories.all())
        categories_dict[category] = subcategories
    
    return {
        'all_categories': main_categories,
        'categories_with_subs': categories_dict,
    }

def home(request):
    categories = Category.objects.filter(parent=None).prefetch_related('subcategories')
    featured_products = Product.objects.filter(featured=True)[:8]
    latest_products = Product.objects.order_by('-created_at')[:8]
    
    return render(request, 'productos/home.html', {
        'categories': categories,
        'featured_products': featured_products,
        'latest_products': latest_products,
    })

class ProductListView(ListView):
    model = Product
    template_name = 'productos/lista_productos.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        sort_param = self.request.GET.get('sort', 'popular')
        products = Product.objects.all()
        
        if sort_param == 'price-low':
            products = products.order_by('price')
        elif sort_param == 'price-high':
            products = products.order_by('-price')
        elif sort_param == 'newest':
            products = products.order_by('-created_at')
        else:  # Default to newest
            products = products.order_by('-created_at')
            
        return products
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_sort'] = self.request.GET.get('sort', 'popular')
        return context

class CategoryView(ListView):
    model = Product
    template_name = 'productos/categorias/category.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        category_slug = self.kwargs.get('category_slug')
        category = get_object_or_404(Category, slug=category_slug)
        
        # Obtener productos de la categoría y todas sus subcategorías
        categories = [category]
        if not category.is_subcategory:
            subcategories = category.subcategories.all()
            categories.extend(subcategories)
        
        # Handle sorting
        sort_param = self.request.GET.get('sort', 'popular')
        products = Product.objects.filter(category__in=categories)
        
        if sort_param == 'price-low':
            products = products.order_by('price')
        elif sort_param == 'price-high':
            products = products.order_by('-price')
        elif sort_param == 'newest':
            products = products.order_by('-created_at')
        else:  # Default to newest
            products = products.order_by('-created_at')
            
        return products
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs.get('category_slug')
        category = get_object_or_404(Category, slug=category_slug)
        
        subcategories = []
        if not category.is_subcategory:
            subcategories = category.subcategories.all()
        
        context.update({
            'category': category,
            'subcategories': subcategories,
            'is_subcategory': category.is_subcategory,
            'current_sort': self.request.GET.get('sort', 'popular'),
        })
        
        return context

class SubCategoryView(ListView):
    model = Product
    template_name = 'productos/categorias/category.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        parent_slug = self.kwargs.get('category_slug')
        subcategory_slug = self.kwargs.get('subcategory_slug')
        
        parent_category = get_object_or_404(Category, slug=parent_slug, parent=None)
        subcategory = get_object_or_404(Category, slug=subcategory_slug, parent=parent_category)
        
        sort_param = self.request.GET.get('sort', 'popular')
        products = Product.objects.filter(category=subcategory)
        
        if sort_param == 'price-low':
            products = products.order_by('price')
        elif sort_param == 'price-high':
            products = products.order_by('-price')
        elif sort_param == 'newest':
            products = products.order_by('-created_at')
        else:  # Default to newest
            products = products.order_by('-created_at')
            
        return products
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        parent_slug = self.kwargs.get('category_slug')
        subcategory_slug = self.kwargs.get('subcategory_slug')
        
        parent_category = get_object_or_404(Category, slug=parent_slug, parent=None)
        subcategory = get_object_or_404(Category, slug=subcategory_slug, parent=parent_category)
        
        context.update({
            'category': subcategory,
            'parent_category': parent_category,
            'is_subcategory': True,
            'current_sort': self.request.GET.get('sort', 'popular'),
        })
        
        return context

def subcategory_by_id(request, subcategory_id):
    """Vista para acceder directamente a una subcategoría por su ID"""
    subcategory = get_object_or_404(Category, id=subcategory_id, parent__isnull=False)
    return redirect('productos:subcategoria', 
                   category_slug=subcategory.parent.slug,
                   subcategory_slug=subcategory.slug)

class ProductDetailView(DetailView):
    """Vista para mostrar el detalle de un producto"""
    model = Product
    template_name = 'productos/detalle/producto.html'
    context_object_name = 'producto'
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Añadir productos relacionados
        producto = self.get_object()
        productos_relacionados = Product.objects.filter(
            category=producto.category
        ).exclude(id=producto.id)[:4]
        
        context.update({
            'productos_relacionados': productos_relacionados,
            'is_in_wishlist': False,  # Implement wishlist functionality if needed
        })
        return context
