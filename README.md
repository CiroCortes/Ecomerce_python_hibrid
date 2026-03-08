# EcoTienda — E-Commerce de Productos Naturales

Proyecto final del Bootcamp de Python · Módulo 8
E-commerce funcional desarrollado con **Django 4.2**, **SQLite** y **Tailwind CSS** (CDN).

---

## Descripción

EcoTienda es una tienda online de productos naturales (hongos medicinales, adaptógenos, superalimentos, aceites y suplementos). Implementa el flujo completo: catálogo → carrito → confirmación de compra, con panel de administración propio para gestionar el inventario.

---

## Requisitos

- Python 3.10+
- pip
- Git

---

## Instalación y ejecución local

```bash
# 1. Clonar el repositorio
git clone <URL_DEL_REPOSITORIO>
cd Proyecto_final_bootcamp

# 2. Crear y activar el entorno virtual
python -m venv env

# Windows
env\Scripts\activate

# macOS / Linux
source env/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Aplicar migraciones
python manage.py migrate

# 5. Poblar la base de datos con datos de ejemplo (5 categorías + 15 productos)
python manage.py seed_db

# 6. Levantar el servidor de desarrollo
python manage.py runserver
```

Abre el navegador en: [http://127.0.0.1:8000](http://127.0.0.1:8000)

> Para resetear los datos de ejemplo: `python manage.py seed_db --flush`

---

## Rutas principales

### Públicas (sin autenticación)

| URL | Descripción |
|-----|-------------|
| `/` | Home — productos destacados ("Imperdibles") |
| `/catalog/` | Catálogo completo con filtros por categoría |
| `/product/<id>/` | Detalle de producto |
| `/nosotros/` | Página informativa |
| `/cart/` | Ver carrito de compras |
| `/accounts/login/` | Iniciar sesión |
| `/accounts/register/` | Registrar nueva cuenta |

### Cliente autenticado

| URL | Descripción |
|-----|-------------|
| `/cart/add/<id>/` | Agregar producto al carrito |
| `/cart/update/<id>/` | Actualizar cantidad en el carrito |
| `/cart/remove/<id>/` | Eliminar producto del carrito |
| `/checkout/` | Confirmar y procesar pedido |
| `/product/<id>/like/` | Marcar/desmarcar favorito |
| `/accounts/logout/` | Cerrar sesión |

### Administrador (requiere `is_staff = True`)

| URL | Descripción |
|-----|-------------|
| `/admin-panel/` | Listado de todos los productos |
| `/admin-panel/nuevo/` | Crear nuevo producto |
| `/admin-panel/editar/<id>/` | Editar producto existente |
| `/admin-panel/eliminar/<id>/` | Eliminar producto (con confirmación) |
| `/admin/` | Django Admin nativo (superusuario) |

---

## Credenciales de prueba

| Rol | Usuario | Contraseña |
|-----|---------|------------|
| Administrador (staff) | `ciroadmin` | `admin123` |
| usuario_prueba (test) | `usuario_prueba`| `user123456` |
| Cliente | Crear con `/accounts/register/` | — |

> El administrador tiene acceso al panel `/admin-panel/` y al Django Admin nativo `/admin/`.

---

## Estructura del proyecto

```
Proyecto_final_bootcamp/
├── ecommerce_project/       # Configuración del proyecto Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── store/                   # App principal
│   ├── models.py            # Category, Product, Order, OrderItem
│   ├── views.py             # Vistas CBV + FBV
│   ├── urls.py              # 15 rutas con namespace 'store'
│   ├── forms.py             # ProductForm (ModelForm)
│   ├── cart.py              # Clase Cart (carrito en sesión)
│   ├── context_processors.py
│   ├── admin.py             # Django Admin: Category, Product, Order
│   └── management/
│       └── commands/
│           └── seed_db.py   # Comando de carga de datos iniciales
├── templates/               # Templates HTML con herencia
│   ├── base.html
│   ├── store/
│   └── registration/
├── static/                  # CSS, JS, imágenes estáticas
├── media/                   # Imágenes subidas por el admin
├── requirements.txt
└── manage.py
```

---

## Funcionalidades implementadas

- Autenticación completa: registro, login, logout con redirecciones
- Roles: cliente (compra) y administrador (gestiona inventario)
- Catálogo paginado con filtros por categoría
- Carrito de compras persistido en sesión (sin BD)
- Actualización de cantidades y eliminación de ítems en el carrito
- Checkout con creación de `Order` + `OrderItem` en BD y descuento de stock
- Precio histórico guardado en cada `OrderItem`
- Panel admin propio (`/admin-panel/`) separado del Django Admin nativo
- Productos "Imperdibles" (destacados) configurables desde el panel
- Sistema de "Favoritos" por usuario (ManyToMany)
- Comando `seed_db` idempotente para datos de demostración
- Validaciones de negocio: precio > 0, stock ≥ 0, cantidad disponible
