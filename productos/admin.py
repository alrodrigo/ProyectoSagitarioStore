from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductImage, ProductFeature, Review

class SubCategoryInline(admin.TabularInline):
    model = Category
    extra = 1
    fields = ('name', 'description', 'image', 'home_image')
    verbose_name = 'Subcategoría'
    verbose_name_plural = 'Subcategorías'

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    verbose_name = 'Imagen del producto'
    verbose_name_plural = 'Imágenes del producto'
    fields = ('image', 'display_image', 'order')
    readonly_fields = ('display_image',)
    
    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="150" height="auto" />', obj.image.url)
        return "No hay imagen"
    display_image.short_description = 'Vista previa'

class ProductFeatureInline(admin.TabularInline):
    model = ProductFeature
    extra = 2
    verbose_name = 'Característica'
    verbose_name_plural = 'Características del producto'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'is_main_category', 'product_count', 'has_home_image', 'display_image')
    list_filter = ('parent',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [SubCategoryInline]
    fields = ('name', 'slug', 'description', 'parent', 'image', 'display_image', 'home_image', 'display_home_image')
    readonly_fields = ('display_image', 'display_home_image')
    
    def is_main_category(self, obj):
        return obj.parent is None
    is_main_category.boolean = True
    is_main_category.short_description = 'Es categoría principal'
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Productos'
    
    def has_home_image(self, obj):
        return bool(obj.home_image)
    has_home_image.boolean = True
    has_home_image.short_description = 'Imagen de inicio'
    
    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return "No hay imagen"
    display_image.short_description = 'Imagen'
    
    def display_home_image(self, obj):
        if obj.home_image:
            return format_html('<img src="{}" width="200" height="auto" />', obj.home_image.url)
        return "No hay imagen para la página principal"
    display_home_image.short_description = 'Vista previa imagen de inicio'
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.order_by('parent', 'name')
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['name'].help_text = 'Nombre visible de la categoría.'
        form.base_fields['slug'].help_text = 'Identificador único para URLs (se genera automáticamente).'
        form.base_fields['description'].help_text = 'Descripción breve de la categoría.'
        form.base_fields['parent'].help_text = 'Si es una subcategoría, seleccione la categoría padre. Dejar vacío si es una categoría principal.'
        form.base_fields['image'].help_text = 'Imagen principal de la categoría. Tamaño recomendado: 800x600px.'
        form.base_fields['home_image'].help_text = 'Imagen destacada para mostrar en la página de inicio. Tamaño recomendado: 1200x600px.'
        return form

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'original_price', 'stock', 'featured', 'is_reservable', 'main_image')
    list_filter = ('category', 'featured', 'is_reservable')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('price', 'original_price', 'stock', 'featured', 'is_reservable')
    inlines = [ProductImageInline, ProductFeatureInline]
    save_on_top = True
    
    fieldsets = (
        ('Información básica', {
            'fields': ('name', 'slug', 'category')
        }),
        ('Detalles del producto', {
            'fields': ('description', 'price', 'original_price', 'stock')
        }),
        ('Opciones de visualización', {
            'fields': ('featured', 'image'),
            'description': 'Configure si el producto debe destacarse en la página principal.'
        }),
        ('Opciones de reserva', {
            'fields': ('is_reservable', 'min_reservation_days'),
            'description': 'Configure si el producto puede ser reservado y por cuántos días mínimo.'
        }),
    )
    
    def main_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return "No hay imagen"
    main_image.short_description = 'Imagen'
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['name'].help_text = 'Nombre del producto que verán los clientes.'
        form.base_fields['slug'].help_text = 'Identificador único para URLs (se genera automáticamente).'
        form.base_fields['category'].help_text = 'Categoría a la que pertenece el producto.'
        form.base_fields['description'].help_text = 'Descripción detallada del producto. Incluya características, medidas, material, etc.'
        form.base_fields['price'].help_text = 'Precio de venta en Bs.'
        form.base_fields['stock'].help_text = 'Cantidad de unidades disponibles.'
        form.base_fields['featured'].help_text = 'Marque esta opción para destacar el producto en la página principal.'
        return form
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si es un producto nuevo
            super().save_model(request, obj, form, change)
            # Mensaje de ayuda después de crear
            self.message_user(request, 
                "¡Producto creado! No olvide añadir imágenes adicionales haciendo clic en '+ Añadir otra Imagen del producto' abajo.")
        else:
            super().save_model(request, obj, form, change)
            if obj.stock <= 3:
                self.message_user(request, 
                    f"¡Atención! El stock del producto '{obj.name}' es bajo ({obj.stock} unidades).", level='WARNING')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating_stars', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('product__name', 'user__username', 'content')
    readonly_fields = ('product', 'user', 'created_at')
    
    def rating_stars(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span style="color: #FFD700;">{}</span>', stars)
    rating_stars.short_description = 'Calificación'
