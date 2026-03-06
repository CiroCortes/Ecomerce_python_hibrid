from .cart import Cart

def cart_processor(request):
    """
    Context processor para que la instancia del carrito 
    esté disponible globalmente en todas las plantillas.
    Permite usar {{ cart|length }} o {{ cart.get_total_price }} en el Navbar.
    """
    return {'cart': Cart(request)}
