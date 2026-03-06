from decimal import Decimal
from django.conf import settings
from .models import Product

class Cart:
    def __init__(self, request):
        """Inicializa el carrito desde la sesión del usuario (anónimo o logueado)."""
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            # Guarda un carrito vacío en la sesión si no existe
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        """Agrega un producto al carrito o actualiza su cantidad."""
        product_id = str(product.id)
        
        # Validar stock disponible
        if quantity > product.stock:
            quantity = product.stock

        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}
        
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
            
            # Re-validar si al sumar excede el stock
            if self.cart[product_id]['quantity'] > product.stock:
                self.cart[product_id]['quantity'] = product.stock
                
        self.save()

    def save(self):
        """Marca la sesión como modificada para asegurar que Django la guarde."""
        self.session.modified = True

    def remove(self, product):
        """Elimina un producto del carrito."""
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def clear(self):
        """Vacia el carrito de la sesión por completo."""
        del self.session['cart']
        self.save()

    def __iter__(self):
        """Itera sobre los items del carrito y obtiene los objetos Product de la BD."""
        product_ids = self.cart.keys()
        # Obtenemos los productos actuales de la base de datos
        products = Product.objects.filter(id__in=product_ids)
        
        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product
            
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """Cuenta la cantidad total de artículos físicos en el carrito."""
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """Calcula el costo total monetario de los productos en el carrito."""
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())
