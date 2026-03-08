from django import forms
from .models import Product, Category


class ProductForm(forms.ModelForm):
    """
    Formulario para crear y editar productos desde el panel de administración.
    Centraliza todas las validaciones de negocio (DRY: reutilizado en crear y editar).
    """

    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'price', 'stock', 'image', 'is_active', 'is_featured']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl bg-gray-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent text-sm transition-colors',
                'placeholder': 'Ej: Aceite de Argán Orgánico',
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl bg-gray-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent text-sm transition-colors',
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl bg-gray-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent text-sm transition-colors resize-none',
                'rows': 4,
                'placeholder': 'Descripción detallada del producto...',
            }),
            'price': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl bg-gray-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent text-sm transition-colors',
                'step': '0.01',
                'min': '0.01',
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl bg-gray-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent text-sm transition-colors',
                'min': '0',
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-brand-50 file:text-brand-700 hover:file:bg-brand-100 transition-colors',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-brand-600 focus:ring-brand-500 border-gray-300 rounded cursor-pointer',
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-brand-600 focus:ring-brand-500 border-gray-300 rounded cursor-pointer',
            }),
        }
        labels = {
            'name': 'Nombre del Producto',
            'category': 'Categoría',
            'description': 'Descripción',
            'price': 'Precio ($)',
            'stock': 'Stock (unidades)',
            'image': 'Imagen del Producto',
            'is_active': 'Producto activo (visible en tienda)',
            'is_featured': 'Imperdible (Destacado en portada)',
        }

    def clean_price(self):
        """Valida que el precio sea mayor que cero."""
        price = self.cleaned_data.get('price')
        if price is not None and price <= 0:
            raise forms.ValidationError('El precio debe ser mayor a $0.')
        return price

    def clean_stock(self):
        """Valida que el stock no sea negativo."""
        stock = self.cleaned_data.get('stock')
        if stock is not None and stock < 0:
            raise forms.ValidationError('El stock no puede ser negativo.')
        return stock
