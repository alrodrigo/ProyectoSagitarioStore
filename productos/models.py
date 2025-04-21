from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
import django.utils.timezone

User = get_user_model()

class Category(models.Model):
    name = models.CharField('Nombre', max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField('Descripción', blank=True)
    created_at = models.DateTimeField('Fecha de creación', default=django.utils.timezone.now)
    updated_at = models.DateTimeField('Fecha de actualización', auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['name']

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField('Nombre', max_length=200)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    description = models.TextField('Descripción')
    details = models.TextField('Detalles del producto', blank=True, null=True)
    price = models.DecimalField('Precio', max_digits=10, decimal_places=2)
    original_price = models.DecimalField('Precio original', max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField('Stock disponible', default=0)
    image = models.ImageField('Imagen principal', upload_to='products/')
    featured = models.BooleanField('Destacado', default=False)
    created_at = models.DateTimeField('Fecha de creación', auto_now_add=True)
    updated_at = models.DateTimeField('Fecha de actualización', auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

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

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['-created_at']

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

