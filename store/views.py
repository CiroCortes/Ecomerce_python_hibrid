from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView
from django.db import transaction
from .models import Product, Order, OrderItem
from .cart import Cart

class ProductListView(ListView):
    """Vista del catálogo inspirada en ecotiendanaturals, usando CBV para mantener DRY."""
    model = Product
    template_name = 'store/product_list.html'
    context_object_name = 'products'
    
    def get_queryset(self):
        # Solo mostrar productos activos en el front
        return Product.objects.filter(is_active=True).order_related() if hasattr(Product.objects, 'order_related') else Product.objects.filter(is_active=True)

class ProductDetailView(DetailView):
    model = Product
    template_name = 'store/product_detail.html'
    context_object_name = 'product'


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

@login_required
def checkout(request):
    """Procesa la compra: Transforma el Carrito (Sesión) en una Orden (BD)."""
    cart = Cart(request)
    
    # Validar que no se pueda comprar un carrito vacío
    if len(cart) == 0:
        messages.warning(request, "Tu carrito está vacío. Agrega productos antes de comprar.")
        return redirect('store:product_list')

    if request.method == 'POST':
        # En una aplicación real, aquí validaríamos la dirección de envío del formulario (address)
        # o procesaríamos la pasarela de pago (Stripe/PayPal/Transbank).
        shipping_address = request.POST.get('address', 'Dirección Pendiente de registro MVP')

        try:
            # Usar atomic para asegurar que si algo falla, no se guarde media orden.
            with transaction.atomic():
                # 1. Crear la Orden padre
                order = Order.objects.create(
                    user=request.user,
                    total_amount=cart.get_total_price(),
                    shipping_address=shipping_address,
                    status='paid' # Asumimos pago exitoso para el flujo MVP
                )
                
                # 2. Transferir los ítems del carrito a OrderItem y descontar Stock
                for item in cart:
                    product = item['product']
                    quantity = item['quantity']
                    
                    # Doble verificación de stock (Race condition protection)
                    # En sistemas concurrentes altos, se usaría select_for_update()
                    if product.stock < quantity:
                        raise ValueError(f"No hay suficiente stock para {product.name}.")
                        
                    # Crear el item de la orden con el precio HISTÓRICO actual
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        price=item['price'],
                        quantity=quantity
                    )
                    
                    # Reducir stock del inventario
                    product.stock -= quantity
                    
                    # Si el stock llega a cero, el flag in_stock dinámico fallará en el frontend
                    product.save()

                # 3. Limpiar carrito de la sesión
                cart.clear()

                messages.success(request, f"¡Gracias por tu compra eco-amigable! El pedido #{order.id} ha sido procesado.")
                return redirect('store:product_list')  # Podría redirigir a una página de "Gracias"
                
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('store:cart_detail')
            
        except Exception as e:
            messages.error(request, "Ocurrió un error al procesar tu pedido. Inténtalo de nuevo.")
            return redirect('store:cart_detail')
            
    # Si es GET, mostramos un formulario de checkout básico en el mismo cart_detail o nueva plantilla
    # Para el flujo MVP rápido, manejaremos el checkout en una ventana modal o directo.
    return redirect('store:cart_detail')
