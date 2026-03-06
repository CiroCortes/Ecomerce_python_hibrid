from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Product
from .cart import Cart

@require_POST
def cart_add(request, product_id):
    """Vista para agregar un producto al carrito, manejada por un formulario POST."""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    # Intentamos obtener la cantidad desde el formulario (por defecto 1)
    try:
        quantity = int(request.POST.get('quantity', 1))
    except ValueError:
        quantity = 1

    # Validaciones básicas de stock y cantidad negativa
    if quantity <= 0:
        messages.error(request, "La cantidad debe ser mayor a 0.")
    elif quantity > product.stock:
        # Forzamos la cantidad al máximo permitido si el stock es superado
        cart.add(product=product, quantity=product.stock, override_quantity=True)
        messages.warning(request, f"¡Atención! Hemos ajustado tu cantidad al stock disponible ({product.stock} unidades de {product.name}).")
    else:
        cart.add(product=product, quantity=quantity)
        messages.success(request, f"¡{product.name} ha sido agregado al carrito con éxito!")

    # Retorna a la página desde la cual el usuario hizo clic en "agregar"
    return redirect(request.META.get('HTTP_REFERER', '/'))


@require_POST
def cart_remove(request, product_id):
    """Vista para eliminar un producto completo del carrito."""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.info(request, f"{product.name} fue eliminado del carrito.")
    
    # Después de borrar algo del carrito, recargamos la vista del carrito
    return redirect('store:cart_detail')


def cart_detail(request):
    """Vista principal que renderiza el template del carrito de compras."""
    cart = Cart(request)
    return render(request, 'store/cart_detail.html', {'cart': cart})
