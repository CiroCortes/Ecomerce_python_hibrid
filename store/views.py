from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import ListView, DetailView
from django.db import transaction
from .models import Product, Order, OrderItem, Category
from .cart import Cart
from .forms import ProductForm
import uuid

# ── Helper de acceso admin ────────────────────────────────────────────────────
# Centralizado aquí para que todos los decoradores lo reutilicen (DRY).
def _is_staff(user):
    return user.is_authenticated and user.is_staff


class ProductListView(ListView):
    """Vista del Home con los imperdibles/más vendidos."""
    model = Product
    template_name = 'store/product_list.html'
    context_object_name = 'products'
    
    def get_queryset(self):
        """
        Lógica híbrida DRY para 'Imperdibles':
        1. Intenta traer los productos marcados manualmente por el admin (is_featured=True).
        2. Si hay menos de 4, rellena los faltantes con los más recientes.
        Devuelve exactamente 4 productos asegurando que la portada siempre se vea viva.
        """
        # 1. Obtener los destacados manuales
        featured = Product.objects.filter(is_active=True, is_featured=True).order_by('-created_at')
        
        # Si ya tenemos 4 o más, devolvemos solo 4
        if featured.count() >= 4:
            return featured[:4]
            
        # 2. Si faltan, calculamos cuántos necesitamos
        needed = 4 - featured.count()
        featured_ids = list(featured.values_list('id', flat=True))
        
        # Obtenemos los más recientes que NO estén ya en los destacados
        recent = Product.objects.filter(is_active=True).exclude(id__in=featured_ids).order_by('-created_at')[:needed]
        
        # Unimos ambas listas (Django en Generic Views permite devolver una lista en lugar de un QuerySet si no hay paginación)
        return list(featured) + list(recent)

class CatalogView(ListView):
    """Vista del catálogo completo con filtros por categoría y paginación."""
    model = Product
    template_name = 'store/catalog.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related('category')
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['current_category'] = self.request.GET.get('category')
        return context

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
def cart_update(request, product_id):
    """Actualiza la cantidad de un producto en el carrito desde el formulario del carrito."""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    try:
        quantity = int(request.POST.get('quantity', 1))
    except ValueError:
        quantity = 1

    if quantity <= 0:
        cart.remove(product)
        messages.info(request, f"{product.name} fue eliminado del carrito.")
    elif quantity > product.stock:
        cart.add(product=product, quantity=product.stock, override_quantity=True)
        messages.warning(request, f"Cantidad ajustada al stock disponible ({product.stock} uds.).")
    else:
        cart.add(product=product, quantity=quantity, override_quantity=True)
        messages.success(request, f"Cantidad de {product.name} actualizada.")

    return redirect('store:cart_detail')


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


def about(request):
    """Vista estática de la página Nosotros."""
    return render(request, 'store/about.html')


def register(request):
    """Registro de nuevo usuario. Tras el alta, inicia sesión automáticamente."""
    # Si el usuario ya está autenticado, no necesita registrarse
    if request.user.is_authenticated:
        return redirect('store:product_list')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Login automático post-registro — mejor UX, sin doble paso
            login(request, user)
            messages.success(request, f'¡Bienvenido/a a EcoTienda, {user.username}! Tu cuenta ha sido creada con éxito.')
            return redirect('store:product_list')
        # Si el formulario es inválido, se re-renderiza con los errores
    else:
        form = UserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


@require_POST
@login_required
def toggle_product_like(request, pk):
    """
    Agrega o quita un producto de los favoritos del usuario (Like).
    Redirige transparentemente a la página desde la que se hizo clic.
    """
    product = get_object_or_404(Product, pk=pk)
    
    if request.user in product.likes.all():
        product.likes.remove(request.user)
        messages.info(request, f'Quitaste "{product.name}" de tus favoritos 🤍')
    else:
        product.likes.add(request.user)
        messages.success(request, f'¡Agregaste "{product.name}" a tus favoritos ❤️!')
        
    return redirect(request.META.get('HTTP_REFERER', 'store:catalog'))


# ══════════════════════════════════════════════════════════════════════════════
# PANEL DE ADMINISTRACIÓN — CRUD de Productos
# Acceso restringido: solo usuarios con is_staff=True
# ══════════════════════════════════════════════════════════════════════════════

@user_passes_test(_is_staff, login_url='login')
def admin_product_list(request):
    """Lista todos los productos para el administrador (activos e inactivos)."""
    products = Product.objects.select_related('category').order_by('-created_at')
    return render(request, 'store/admin_product_list.html', {'products': products})


@user_passes_test(_is_staff, login_url='login')
def admin_product_create(request):
    """Crea un nuevo producto. Genera el SKU automáticamente."""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            # Generamos un SKU único internamente — el admin no lo necesita gestionar
            product.sku = f"ECO-{uuid.uuid4().hex[:8].upper()}"
            product.save()
            messages.success(request, f'Producto "{product.name}" creado correctamente.')
            return redirect('store:admin_product_list')
    else:
        form = ProductForm()

    return render(request, 'store/admin_product_form.html', {
        'form': form,
        'action_title': 'Nuevo Producto',
        'btn_label': 'Crear Producto',
    })


@user_passes_test(_is_staff, login_url='login')
def admin_product_edit(request, pk):
    """Edita un producto existente. Reutiliza el mismo form y template que crear (DRY)."""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Producto "{product.name}" actualizado correctamente.')
            return redirect('store:admin_product_list')
    else:
        form = ProductForm(instance=product)

    return render(request, 'store/admin_product_form.html', {
        'form': form,
        'product': product,
        'action_title': f'Editar: {product.name}',
        'btn_label': 'Guardar Cambios',
    })


@user_passes_test(_is_staff, login_url='login')
def admin_product_delete(request, pk):
    """Elimina un producto tras confirmación explícita del administrador."""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f'Producto "{name}" eliminado correctamente.')
        return redirect('store:admin_product_list')

    return render(request, 'store/admin_product_confirm_delete.html', {'product': product})
