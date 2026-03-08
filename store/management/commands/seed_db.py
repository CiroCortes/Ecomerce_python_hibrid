"""
Management command: python manage.py seed_db

Pobla la base de datos con:
  - 5 categorías de productos naturales
  - 15 productos con datos realistas
  - Idempotente: usa get_or_create, se puede ejecutar varias veces sin duplicar datos
  - Compatible con PostgreSQL y SQLite

Imágenes: coloca los archivos en media/products/ con los nombres indicados abajo.
"""

from django.core.management.base import BaseCommand
from django.utils.text import slugify
from store.models import Category, Product
from decimal import Decimal


# ── Datos de Categorías ──────────────────────────────────────────────────────
CATEGORIES = [
    {
        'name': 'Hongos Medicinales',
        'slug': 'hongos-medicinales',
        'description': 'Hongos funcionales certificados con propiedades adaptogénicas y neuroprotectoras.',
    },
    {
        'name': 'Adaptógenos y Superraíces',
        'slug': 'adaptogenos-superraices',
        'description': 'Plantas y raíces milenarias que ayudan al cuerpo a adaptarse al estrés.',
    },
    {
        'name': 'Superalimentos',
        'slug': 'superalimentos',
        'description': 'Alimentos de alta densidad nutricional en formato concentrado.',
    },
    {
        'name': 'Aceites y Aromaterapia',
        'slug': 'aceites-aromaterapia',
        'description': 'Aceites esenciales puros y aceites vegetales de primera presión en frío.',
    },
    {
        'name': 'Suplementos Naturales',
        'slug': 'suplementos-naturales',
        'description': 'Suplementos de origen natural para optimizar la salud integral.',
    },
]

# ── Datos de Productos ───────────────────────────────────────────────────────
# image: nombre del archivo que debes colocar en media/products/
PRODUCTS = [
    # ── Hongos Medicinales ──────────────────────────────────────────────
    {
        'category_slug': 'hongos-medicinales',
        'name': 'Melena de León Premium',
        'sku': 'ECO-HM-001',
        'description': (
            'Hericium erinaceus 100% puro en polvo. Cultivado orgánicamente y libre de aditivos. '
            'Reconocido por sus propiedades neuroprotectoras y su capacidad de estimular el factor de crecimiento nervioso (NGF). '
            'Ideal para mejorar la concentración, la memoria y la claridad mental. '
            '60 g por envase. Certificado orgánico.'
        ),
        'price': Decimal('24900'),
        'stock': 45,
        'image': 'products/melena_de_leon.jpg',
        'is_active': True,
    },
    {
        'category_slug': 'hongos-medicinales',
        'name': 'Reishi Supremo (Polvo)',
        'sku': 'ECO-HM-002',
        'description': (
            'Ganoderma lucidum de doble extracción: agua + alcohol para máxima biodisponibilidad de beta-glucanos y triterpenos. '
            'Conocido como el "hongo de la inmortalidad" en la medicina tradicional china. '
            'Apoya el sistema inmune, reduce el estrés crónico y favorece el sueño reparador. '
            '60 g por envase.'
        ),
        'price': Decimal('22900'),
        'stock': 38,
        'image': 'products/reishi_supremo.jpg',
        'is_active': True,
    },
    {
        'category_slug': 'hongos-medicinales',
        'name': 'Cordyceps Energético',
        'sku': 'ECO-HM-003',
        'description': (
            'Cordyceps militaris cultivado en sustrato vegetal (sin larvas). '
            'Rico en cordicepina, un compuesto que aumenta la producción de ATP celular. '
            'Utilizado por deportistas para mejorar la resistencia aeróbica, reducir la fatiga y optimizar el rendimiento físico. '
            '60 g por envase.'
        ),
        'price': Decimal('26900'),
        'stock': 30,
        'image': 'products/cordyceps_energetico.jpg',
        'is_active': True,
    },
    {
        'category_slug': 'hongos-medicinales',
        'name': 'Chaga Antioxidante',
        'sku': 'ECO-HM-004',
        'description': (
            'Inonotus obliquus silvestre de Siberia, extraído del abedul. '
            'Uno de los antioxidantes más potentes de la naturaleza: alto contenido en melanina, betulinol y polisacáridos. '
            'Apoya la respuesta inmune, la salud digestiva y la protección celular frente al estrés oxidativo. '
            '60 g por envase.'
        ),
        'price': Decimal('23900'),
        'stock': 25,
        'image': 'products/chaga_antioxidante.jpg',
        'is_active': True,
    },
    # ── Adaptógenos y Superraíces ───────────────────────────────────────
    {
        'category_slug': 'adaptogenos-superraices',
        'name': 'Ashwagandha KSM-66',
        'sku': 'ECO-AD-001',
        'description': (
            'Extracto de raíz de Withania somnifera con 5% de withanólidos (extracto KSM-66, el más estudiado clínicamente). '
            'Reduce el cortisol, mejora la respuesta al estrés, aumenta la testosterona en hombres y mejora la función tiroidea. '
            'Cápsulas vegetales de 500 mg. 60 cápsulas por envase.'
        ),
        'price': Decimal('18900'),
        'stock': 55,
        'image': 'products/ashwagandha_ksm66.jpg',
        'is_active': True,
    },
    {
        'category_slug': 'adaptogenos-superraices',
        'name': 'Maca Andina Negra Premium',
        'sku': 'ECO-AD-002',
        'description': (
            'Lepidium meyenii cultivada sobre los 4.200 m. de altitud en los Andes del Perú. '
            'La maca negra es la variedad más potente, asociada al aumento de la libido, la fertilidad y la energía sostenida. '
            'Polvo gelatinizado para mejor absorción y sin molestias digestivas. '
            '250 g por envase.'
        ),
        'price': Decimal('15900'),
        'stock': 60,
        'image': 'products/maca_andina_negra.jpg',
        'is_active': True,
    },
    {
        'category_slug': 'adaptogenos-superraices',
        'name': 'Rhodiola Rosea 3% Rosavinas',
        'sku': 'ECO-AD-003',
        'description': (
            'Extracto estandarizado de Rhodiola rosea con 3% de rosavinas y 1% de salidrosida. '
            'Adaptógeno siberiano con evidencia clínica en reducción de fatiga mental, mejora del humor y apoyo al rendimiento cognitivo bajo estrés. '
            '60 cápsulas vegetales de 400 mg.'
        ),
        'price': Decimal('17900'),
        'stock': 40,
        'image': 'products/rhodiola_rosea.jpg',
        'is_active': True,
    },
    # ── Superalimentos ──────────────────────────────────────────────────
    {
        'category_slug': 'superalimentos',
        'name': 'Espirulina Orgánica',
        'sku': 'ECO-SA-001',
        'description': (
            'Arthrospira platensis cultivada en agua dulce sin pesticidas. '
            'Contiene hasta un 70% de proteína completa, vitamina B12, hierro, betacaroteno y ficocianina. '
            'Ideal para vegetarianos y veganos como fuente de nutrición densa. '
            'Comprimidos de 500 mg. 120 comprimidos por envase.'
        ),
        'price': Decimal('12900'),
        'stock': 80,
        'image': 'products/espirulina_organica.jpg',
        'is_active': True,
    },
    {
        'category_slug': 'superalimentos',
        'name': 'Clorela Detox Premium',
        'sku': 'ECO-SA-002',
        'description': (
            'Chlorella vulgaris con pared celular rota (cracked cell) para máxima absorción. '
            'Rica en clorofila, proteína completa y el Factor de Crecimiento de Clorela (CGF). '
            'Reconocida por su capacidad de unirse a metales pesados y facilitar su excreción. '
            '120 comprimidos de 500 mg.'
        ),
        'price': Decimal('13900'),
        'stock': 65,
        'image': 'products/clorela_detox.jpg',
        'is_active': True,
    },
    {
        'category_slug': 'superalimentos',
        'name': 'Moringa Oleifera Orgánica',
        'sku': 'ECO-SA-003',
        'description': (
            'Hojas de Moringa oleifera deshidratadas a baja temperatura para preservar sus nutrientes. '
            'Contiene más vitamina C que las naranjas, más calcio que la leche y más hierro que la espinaca. '
            'Polvo de sabor suave, ideal para añadir a batidos, jugos y comidas. '
            '200 g por envase.'
        ),
        'price': Decimal('11900'),
        'stock': 70,
        'image': 'products/moringa_organica.jpg',
        'is_active': True,
    },
    # ── Aceites y Aromaterapia ─────────────────────────────────────────
    {
        'category_slug': 'aceites-aromaterapia',
        'name': 'Aceite Esencial de Lavanda',
        'sku': 'ECO-AE-001',
        'description': (
            'Lavandula angustifolia destilada por arrastre de vapor en Provenza, Francia. '
            '100% puro, sin cortes ni solventes. '
            'El aceite más versátil de la aromaterapia: ansiolítico, cicatrizante, antiinflamatorio y promotor del sueño. '
            'Apto para uso tópico diluido y difusión. '
            'Frasco de 15 ml con gotero de acero inoxidable.'
        ),
        'price': Decimal('9900'),
        'stock': 90,
        'image': 'products/aceite_lavanda.jpg',
        'is_active': True,
    },
    {
        'category_slug': 'aceites-aromaterapia',
        'name': 'Aceite de Argán Puro (Cosmético)',
        'sku': 'ECO-AE-002',
        'description': (
            'Argania spinosa prensada en frío, sin refinado ni decoloración. '
            'Rico en ácidos oleico y linoleico, vitamina E y escualeno. '
            'Hidratante facial, corporal y capilar de alta penetración. '
            'No comedogénico, ideal para pieles sensibles y maduras. '
            '30 ml en envase de vidrio oscuro con cuentagotas.'
        ),
        'price': Decimal('16900'),
        'stock': 50,
        'image': 'products/aceite_argan.jpg',
        'is_active': True,
    },
    # ── Suplementos Naturales ──────────────────────────────────────────
    {
        'category_slug': 'suplementos-naturales',
        'name': 'Vitamina D3 + K2 (MK-7)',
        'sku': 'ECO-SN-001',
        'description': (
            'Sinergia de Vitamina D3 (colecalciferol, 2000 UI) + Vitamina K2 en forma MK-7 (100 mcg), '
            'la combinación más biodisponible para favorecer la fijación del calcio en los huesos '
            'y proteger las arterias. Base de aceite de oliva virgen extra para mejor absorción. '
            '60 cápsulas blandas.'
        ),
        'price': Decimal('14900'),
        'stock': 75,
        'image': 'products/vitamina_d3_k2.jpg',
        'is_active': True,
    },
    {
        'category_slug': 'suplementos-naturales',
        'name': 'Omega-3 Krill Antártico',
        'sku': 'ECO-SN-002',
        'description': (
            'Aceite de krill antártico (Euphasia superba) con 250 mg de EPA+DHA en forma de fosfolípidos '
            '— hasta 5 veces más absorbibles que el omega-3 de pescado convencional. '
            'Incluye astaxantina natural (antioxidante), sin sabor a pescado. '
            '60 cápsulas blandas.'
        ),
        'price': Decimal('21900'),
        'stock': 35,
        'image': 'products/omega3_krill.jpg',
        'is_active': True,
    },
    {
        'category_slug': 'suplementos-naturales',
        'name': 'Probiótico Flora Vital 50B',
        'sku': 'ECO-SN-003',
        'description': (
            '50 mil millones de UFC por cápsula, 10 cepas probióticas complementarias incluyendo '
            'Lactobacillus acidophilus, Bifidobacterium longum y Lactobacillus rhamnosus GG. '
            'Con FOS (prebiótico) para potenciar la colonización. '
            'Cápsulas con cubierta entérica para garantizar llegada al intestino grueso. '
            '30 cápsulas por envase. Requiere refrigeración.'
        ),
        'price': Decimal('19900'),
        'stock': 42,
        'image': 'products/probiotico_flora_vital.jpg',
        'is_active': True,
    },
]


class Command(BaseCommand):
    help = 'Puebla la base de datos con categorías y 15 productos naturales de EcoTienda.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush',
            action='store_true',
            help='Elimina todos los productos y categorías antes de sembrar.',
        )

    def handle(self, *args, **options):
        if options['flush']:
            self.stdout.write(self.style.WARNING('⚠  Eliminando datos existentes...'))
            Product.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write(self.style.WARNING('   Datos eliminados.\n'))

        # ── 1. Crear Categorías ─────────────────────────────────────────
        self.stdout.write(self.style.MIGRATE_HEADING('📂 Creando categorías...'))
        category_map = {}
        for cat_data in CATEGORIES:
            cat, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={
                    'name': cat_data['name'],
                    'description': cat_data['description'],
                }
            )
            status = '✓ Creada' if created else '→ Ya existe'
            self.stdout.write(f'   {status}: {cat.name}')
            category_map[cat_data['slug']] = cat

        # ── 2. Crear Productos ──────────────────────────────────────────
        self.stdout.write(self.style.MIGRATE_HEADING('\n📦 Creando productos...'))
        created_count = 0
        skipped_count = 0

        for prod_data in PRODUCTS:
            category = category_map.get(prod_data['category_slug'])
            product, created = Product.objects.get_or_create(
                sku=prod_data['sku'],
                defaults={
                    'category': category,
                    'name': prod_data['name'],
                    'description': prod_data['description'],
                    'price': prod_data['price'],
                    'stock': prod_data['stock'],
                    'image': prod_data['image'],
                    'is_active': prod_data['is_active'],
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f'   ✓ {product.sku} — {product.name}')
            else:
                skipped_count += 1
                self.stdout.write(self.style.WARNING(f'   → {product.sku} ya existe, omitido.'))

        # ── Resumen ─────────────────────────────────────────────────────
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'✅ Seed completado: {created_count} productos creados, {skipped_count} omitidos.'
        ))
        self.stdout.write(
            '   Recuerda colocar las imágenes en media/products/ '
            'con los nombres indicados en el script.'
        )
