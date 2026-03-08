from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    # Home & Catalog routes
    path('', views.ProductListView.as_view(), name='product_list'),
    path('catalog/', views.CatalogView.as_view(), name='catalog'),
    path('nosotros/', views.about, name='about'),
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('product/<int:pk>/like/', views.toggle_product_like, name='toggle_like'),

    # Cart routes
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),

    # Checkout route
    path('checkout/', views.checkout, name='checkout'),

    # Auth: registro (login/logout los provee django.contrib.auth.urls en el proyecto)
    path('accounts/register/', views.register, name='register'),

    # ── Panel de Administración de Productos (solo staff) ──────────────────────
    path('admin-panel/', views.admin_product_list, name='admin_product_list'),
    path('admin-panel/nuevo/', views.admin_product_create, name='admin_product_create'),
    path('admin-panel/editar/<int:pk>/', views.admin_product_edit, name='admin_product_edit'),
    path('admin-panel/eliminar/<int:pk>/', views.admin_product_delete, name='admin_product_delete'),
]


