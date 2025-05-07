from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
import django.utils.timezone
from django.core.cache import cache
from django.db.models import Index

User = get_user_model()

class Category(models.Model):
    name = models.CharField('Nombre', max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField('Descripción', blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, 
                             related_name='subcategories', verbose_name='Categoría padre')
    image = models.ImageField('Imagen', upload_to='categories/', blank=True, null=True)
    home_image = models.ImageField('Imagen para página de inicio', 
                                 upload_to='categories/home/', 
                                 blank=True, 
                                 null=True,
                                 help_text='Imagen específica para mostrar en la página de inicio. Si no se proporciona, se usará la imagen principal.')
    created_at = models.DateTimeField('Fecha de creación', default=django.utils.timezone.now)
    updated_at = models.DateTimeField('Fecha de actualización', auto_now=True)

    def save(self, *args, **kwargs):
        # Siempre generar/actualizar el slug basado en el nombre actual
        self.slug = slugify(self.name.lower())  # Aseguramos que el slug esté en minúsculas y actualizado
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('productos:categoria', kwargs={'category_slug': self.slug})
    
    @property
    def is_subcategory(self):
        """Determina si esta categoría es una subcategoría"""
        return self.parent is not None
    
    @property
    def main_category(self):
        """Retorna la categoría principal (de nivel superior) para esta categoría"""
        if self.parent:
            return self.parent.main_category
        return self

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['name']

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    description = models.TextField()
    details = models.TextField('Detalles del producto', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField('Precio original', max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.IntegerField(default=0)
    image = models.ImageField('Imagen principal', upload_to='products/')
    featured = models.BooleanField('Destacado', default=False)
    is_active = models.BooleanField(default=True, db_index=True)
    is_reservable = models.BooleanField('Disponible para reserva', default=False, 
                                      help_text='Indica si este producto puede ser reservado')
    min_reservation_days = models.PositiveIntegerField('Días mínimos de reserva', default=3,
                                                    help_text='Tiempo mínimo en días requerido para la reserva')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['price']),
            models.Index(fields=['is_active', 'stock']),
        ]
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        # Invalidar caché al guardar
        cache.delete(f'product_{self.id}')
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Invalidar caché al eliminar
        cache.delete(f'product_{self.id}')
        super().delete(*args, **kwargs)

    @property
    def discount_percentage(self):
        if self.original_price and self.original_price > self.price:
            return int(((self.original_price - self.price) / self.original_price) * 100)
        return 0

    @property
    def rating(self):
        reviews = self.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0

    @property
    def review_count(self):
        return self.reviews.count()

    @property
    def is_available(self):
        return self.is_active and self.stock > 0

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='additional_images')
    image = models.ImageField('Imagen', upload_to='products/')
    order = models.PositiveIntegerField('Orden', default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Imagen de producto'
        verbose_name_plural = 'Imágenes de productos'

class ProductFeature(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='features')
    description = models.CharField('Descripción', max_length=255)

    class Meta:
        verbose_name = 'Característica'
        verbose_name_plural = 'Características'

    def __str__(self):
        return self.description

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    content = models.TextField('Contenido')
    created_at = models.DateTimeField('Fecha de creación', auto_now_add=True)

    class Meta:
        verbose_name = 'Reseña'
        verbose_name_plural = 'Reseñas'
        ordering = ['-created_at']

    def __str__(self):
        user_name = self.user.get_full_name() if self.user else 'Usuario anónimo'
        return f'Reseña de {user_name} para {self.product.name}'

