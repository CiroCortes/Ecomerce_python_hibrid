# Development Guidelines

## 1. Architecture & Stack
*   **Backend framework:** Django 4.2+ (Python)
*   **Database:** PostgreSQL (with Docker for local development)
*   **Frontend:** Tailwind CSS (via CDN) + Django Templates
*   **Authentication:** Session-based (Django default) + Custom logic for views.
*   **Environment Config:** `python-decouple` (`.env`)

## 2. Coding Standards (Python/Django)
*   **PEP 8:** Strict adherence to PEP 8 standards. Use `black` for auto-formatting.
*   **DRY (Don't Repeat Yourself):** Reuse code via Template Tags, Base templates, and shared utilities.
*   **Naming Conventions:**
    *   `snake_case` for variables, functions, fields, and modules.
    *   `PascalCase` (CamelCase) for Classes (Models, Views).
    *   `UPPER_CASE` for constants.
*   **Views:** Prioritize Class-Based Views (CBV) for CRUD operations and generic pages.

## 3. Project Structure
*   The primary app will be named `store`.
*   Templates will be organized logically: `templates/store/`, `templates/base.html`, etc.
*   Static files (CSS, JS, Images) must be placed in a central `static/` directory.

## 4. Git Flow (Desarrollo)
*   Mantener la rama `main` (o `master`) siempre estable y funcional.
*   No realizar commits directos a `main` si implican nuevas funcionalidades grandes; usar ramas, aunque para este proyecto local el enfoque será iterativo paso a paso.
*   Mensajes de commit claros y descriptivos (ej. `feat: add Product model`, `fix: correct cart total calculation`).

## 5. Deployment Readiness
*   Must maintain a functional `requirements.txt`.
*   Must provide a `Dockerfile` and `docker-compose.yml` for easy replication.
*   Must prepare configurations suitable for Render (Gunicorn, Whitenoise for static files).
