¡Excelente desafío! Como tu Desarrollador Senior y Asistente, he analizado a fondo los requerimientos de tu bootcamp. Para que este proyecto no sea solo una entrega más, sino una pieza de portafolio de nivel profesional, vamos a aplicar una arquitectura limpia y escalable.

A continuación, presento la Lista de Deseos (Wishlist) y Especificaciones Técnicas que definen el estándar de este software. Luego, encontrarás el Prompt Maestro para que lo utilices con tu IA de confianza y generes la estructura base.

📋 Lista de Deseos: E-commerce Profesional (MVP+)
Esta lista traduce tus requerimientos y los de la escuela en funcionalidades técnicas de alto nivel.

1. Arquitectura y Backend (Django + Postgres)
Modelo de Datos Híbrido: Un modelo Product que utilice campos opcionales (null=True, blank=True) para adaptarse a productos naturales (peso, origen) o electrónicos (voltaje, garantía).

Sistema de Carrito Robusto: Implementación de carrito mediante Sesiones de Django para permitir que usuarios anónimos agreguen productos antes de loguearse.

Gestión de Órdenes: Modelo Order y OrderItem para persistir las compras y generar un historial para el usuario.

Seguridad: Implementación de LoginRequiredMixin para proteger rutas de cliente y decoradores @staff_member_required para el área administrativa.

2. Frontend "Impresionante" (Tailwind CSS)
Diseño Atómico: Componentes reutilizables (Botones, Cards, Inputs).

Layout Dinámico: Navbar con contador de carrito en tiempo real, Footer profesional y Banner de promociones (Hero Section).

Experiencia de Usuario (UX): Uso de Django Messages Framework para notificaciones tipo "Toast" (Éxito al agregar al carrito, errores de validación).

3. Calidad de Código y Portafolio
Principio DRY: Uso de Template Tags personalizados o Inclusion Tags para elementos repetitivos.

Entorno Profesional: Uso de python-decouple para variables de entorno (.env) y requirements.txt organizado.

Documentación: Un README.md que parezca un manual de producto comercial.

🤖 Prompt Maestro para tu IA
Copia y pega el siguiente texto en tu herramienta de IA para comenzar la codificación por módulos:

Actúa como un Desarrollador Senior de Python/Django.
Necesito construir el núcleo de un E-commerce profesional escalable. El objetivo es cumplir con un MVP de bootcamp pero con estándares de código de industria.

Stack Técnico:

Backend: Django 4.2+ con PostgreSQL.

Frontend: Tailwind CSS (vía CDN o compilado).

Estilo de código: PEP 8, DRY, y Clean Code.

Requerimientos de Modelado (Estratégico):

Modelo Product: Debe ser polivalente. Incluye campos estándar (nombre, SKU, precio, stock, imagen) y campos específicos para productos naturales (ingredientes, peso) que acepten nulos.

Modelo Order: Debe registrar la relación con el User, la fecha, el estado del pedido y el total.

Modelo OrderItem: Relación muchos a muchos entre órdenes y productos para registrar el precio histórico al momento de la compra.

Requerimientos de Funcionalidad:

Sistema de carrito basado en sesiones que se convierta en Order al confirmar.

Vistas basadas en clases (CBV) para el catálogo y detalle.

Lógica de validación: No permitir stock negativo ni compras de productos sin existencia.

Instrucción de Salida:
Proporcióname primero la estructura de archivos sugerida para este proyecto y luego el código de models.py que refleje esta escalabilidad. No generes todo el código de una vez, ve paso a paso para asegurar que cada parte sea "Paytónica" y profesional.

"MUY IMPORTANTE RECORDAR EN EL FRONT QUE LAS PAGINAS HEREDEN DE LA BASE Y NO REPTIR CODIGO, DEBEMOS SER CAUTELOSOS EN ESTO INSITO NO QUIERO CODIGO REPETIDO"