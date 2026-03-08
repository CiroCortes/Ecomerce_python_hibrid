from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal

class Category(models.Model):
    """
    Categoría para organizar los productos del catálogo.
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    slug = models.SlugField(max_length=100, unique=True, help_text="URL amigable")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    
    class Meta:
        ordering = ['name']
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.name

class Product(models.Model):
    """
    Modelo de Producto Híbrido:
    Permite almacenar tanto productos genéricos, físicos (peso, ingredientes) 
    o electrónicos (voltaje, garantía) sin necesidad de tablas extra, 
    usando campos anulables.
    """
    # Campos Core (Obligatorios para todo producto)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Categoría")
    name = models.CharField(max_length=200, verbose_name="Nombre")
    sku = models.CharField(max_length=50, unique=True, verbose_name="SKU")
    description = models.TextField(verbose_name="Descripción")
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], verbose_name="Precio")
    stock = models.PositiveIntegerField(default=0, verbose_name="Stock Disponible")
    image = models.ImageField(upload_to='products/', null=True, blank=True, verbose_name="Imagen")
    
    # Metadatos para SEO y control interno
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    is_featured = models.BooleanField(default=False, verbose_name="Imperdible (Destacado)")
    likes = models.ManyToManyField(User, related_name='liked_products', blank=True, verbose_name="Favoritos")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # --- CAMPOS ESPECÍFICOS (Opcionales) ---
    
    # Para productos naturales/comida
    ingredients = models.TextField(null=True, blank=True, help_text="Solo para productos consumibles.", verbose_name="Ingredientes")
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Peso en Kg para envíos.", verbose_name="Peso (Kg)")
    
    # Para productos electrónicos
    voltage = models.CharField(max_length=50, null=True, blank=True, help_text="Ej: 110V, 220V, Bi-volt.", verbose_name="Voltaje")
    warranty_months = models.PositiveIntegerField(null=True, blank=True, help_text="Meses de garantía.", verbose_name="Garantía (Meses)")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        return f"{self.sku} - {self.name}"

    @property
    def in_stock(self):
        return self.stock > 0


class Order(models.Model):
    """
    Modelo para registrar las compras de los usuarios.
    """
    STATUS_CHOICES = (
        ('pending', 'Pendiente'),
        ('paid', 'Pagado'),
        ('shipped', 'Enviado'),
        ('cancelled', 'Cancelado'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name="Cliente")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Estado")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Total")
    
    # Datos de facturación/envío simples para el MVP
    shipping_address = models.TextField(verbose_name="Dirección de Envío")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Orden"
        verbose_name_plural = "Órdenes"

    def __str__(self):
        return f"Orden #{self.id} - {self.user.username}"


class OrderItem(models.Model):
    """
    Detalle de la orden. Relaciona Productos con Órdenes guardando una 'foto' del precio original.
    """
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name="Orden")
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.SET_NULL, null=True, verbose_name="Producto")
    
    # Guardamos el precio al momento de la compra, por si el producto sube de precio después.
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Unitario")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Cantidad")

    class Meta:
        verbose_name = "Ítem de Orden"
        verbose_name_plural = "Ítems de Orden"

    def __str__(self):
        return f"{self.quantity} x {self.product.name if self.product else 'Producto Eliminado'}"

    def get_cost(self):
        return self.price * self.quantity
