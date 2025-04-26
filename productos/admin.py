from django.contrib import admin
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

class ProductFeatureInline(admin.TabularInline):
    model = ProductFeature
    extra = 2

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'is_main_category', 'product_count', 'has_home_image')
    list_filter = ('parent',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [SubCategoryInline]
    fields = ('name', 'slug', 'description', 'parent', 'image', 'home_image')
    
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
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.order_by('parent', 'name')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'featured')
    list_filter = ('category', 'featured')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductFeatureInline]

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('product__name', 'user__username', 'content')
