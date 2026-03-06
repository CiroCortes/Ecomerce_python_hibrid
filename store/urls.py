from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    # Catalog routes
    path('', views.ProductListView.as_view(), name='product_list'),
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    
    # Cart routes
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    
    # Checkout route
    path('checkout/', views.checkout, name='checkout'),
]
