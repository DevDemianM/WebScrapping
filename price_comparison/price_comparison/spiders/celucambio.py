import scrapy
import json
import re
from urllib.parse import urljoin
from price_comparison.items import PriceComparisonItem

class CelucambioSpider(scrapy.Spider):
    name = "celucambio"
    allowed_domains = ["celucambio.com"]
    start_urls = [
        "https://celucambio.com/collections/iphone",
        "https://celucambio.com/collections/moviles",
        "https://celucambio.com/collections/ipad",
        "https://celucambio.com/collections/accesorios"
    ]

    def parse(self, response):
        # Extraer links de productos de la página de colección
        # Buscar links que apunten a /products/ pero excluir los de navegación/footer
        product_links = response.css('a[href*="/products/"]::attr(href)').getall()
        
        # Filtrar links únicos
        seen_urls = set()
        for link in product_links:
            if link and '/products/' in link and '/collections/' not in link:
                # Construir URL absoluta
                product_url = urljoin(response.url, link)
                
                # Evitar duplicados
                if product_url not in seen_urls:
                    seen_urls.add(product_url)
                    yield scrapy.Request(
                        url=product_url,
                        callback=self.parse_product_detail
                    )
        
        self.logger.info(f"✅ Encontrados {len(seen_urls)} productos únicos en {response.url}")
        
        # Paginación: buscar link "Siguiente" o page=N
        next_page = response.css('a[rel="next"]::attr(href)').get()
        if not next_page:
            # Buscar enlaces con ?page=
            page_links = response.css('a[href*="?page="]::attr(href)').getall()
            if page_links:
                # Tomar el último que generalmente es "Siguiente"
                for link in reversed(page_links):
                    if 'page=' in link:
                        next_page = link
                        break
        
        if next_page:
            self.logger.info(f"📄 Siguiente página encontrada: {next_page}")
            yield scrapy.Request(
                url=urljoin(response.url, next_page),
                callback=self.parse
            )

    def extract_variants_from_json(self, response):
        """Extrae variantes desde JSON embebido - formato Celucambio"""
        scripts = response.css('script:not([src])::text').getall()
        
        for script in scripts:
            # Celucambio tiene un JSON con variants que incluye: id, price, name, public_title
            if '"variants"' in script and '"price"' in script and '"name"' in script:
                try:
                    # Buscar el array de variants directamente
                    variants_match = re.search(r'"variants"\s*:\s*\[({.*?})\]', script, re.DOTALL)
                    if not variants_match:
                        # Probar patron alternativo
                        variants_match = re.search(r'"variants"\s*:\s*(\[.*?\])', script, re.DOTALL)
                    
                    if variants_match:
                        variants_str = variants_match.group(1)
                        
                        # Si capturamos solo un objeto, lo envolvemos en array
                        if not variants_str.startswith('['):
                            variants_str = f'[{variants_str}]'
                        
                        # Limpiar y parsear
                        variants = json.loads(variants_str)
                        
                        if variants and isinstance(variants, list):
                            self.logger.info(f"✅ Variantes encontradas en JSON Celucambio: {len(variants)}")
                            return variants
                            
                except Exception as e:
                    self.logger.debug(f"Error parseando JSON Celucambio: {e}")
                    continue
        
        return []

    def parse_product_detail(self, response):
        product_name = response.css('h1.product__title::text, h1::text').get()
        
        if not product_name:
            self.logger.warning(f"No se pudo extraer nombre de {response.url}")
            return
        
        product_name = product_name.strip().upper()
        
        # Extraer variantes
        variants = self.extract_variants_from_json(response)
        
        if variants:
            items_generados = 0
            for variant in variants:
                # El precio puede venir en dos formatos:
                # 1. Número directo: "price": 139990000
                # 2. Objeto: "price": {"amount": 1399900.0, "currencyCode": "COP"}
                price_data = variant.get('price', 0)
                
                if isinstance(price_data, dict):
                    # Formato: {"amount": 1399900.0, "currencyCode": "COP"}
                    price_cents = int(price_data.get('amount', 0) * 100)  # Convertir a centavos
                elif isinstance(price_data, (int, float)):
                    # Formato directo en centavos
                    price_cents = int(price_data)
                else:
                    continue
                
                if not price_cents:
                    continue
                
                # Precio en centavos (dividir por 100)
                price = f"${price_cents // 100:,}".replace(',', '.')
                
                # Usar "public_title" si existe, sino "name"
                variant_title = variant.get('public_title') or variant.get('name', '') or variant.get('title', '')
                
                if variant_title:
                    # El título puede venir en formato: "Blanco / Como Nuevo / 128GB"
                    # O en formato completo: "iPhone 13 - Blanco / Como Nuevo / 128GB"
                    if ' - ' in variant_title and product_name in variant_title.upper():
                        # Ya incluye el nombre del producto
                        name_full = variant_title.upper()
                    else:
                        # Solo tiene las variantes
                        name_full = f"{product_name} - {variant_title.upper()}"
                else:
                    name_full = product_name
                
                item = PriceComparisonItem()
                item['name'] = name_full
                item['price'] = price
                items_generados += 1
                yield item
            
            if items_generados > 0:
                self.logger.info(f"✅ Extraídas {items_generados} variantes de {product_name}")
        else:
            self.logger.warning(f"No se pudo extraer precio de {product_name} ({response.url})")
