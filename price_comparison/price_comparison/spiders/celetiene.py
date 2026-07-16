import scrapy
import json
import re
from urllib.parse import urljoin
from price_comparison.items import PriceComparisonItem

class CeletieneSpider(scrapy.Spider):
    name = "celetiene"
    allowed_domains = ["celetiene.co"]
    start_urls = [
        "https://celetiene.co/collections/apple",
        "https://celetiene.co/collections/samsung",
        "https://celetiene.co/collections/xiaomi",
        "https://celetiene.co/collections/celulares"
    ]

    def parse(self, response):
        productos = response.css('div.product-card')
        
        for producto in productos:
            # Solo excluir "Disponible Pronto", permitir productos sin badge o con "Oferta"
            badge = producto.css('.badge::text').get()
            if badge and "Disponible Pronto" in badge:
                continue
            
            product_link = producto.css('a::attr(href)').get()
            if product_link:
                product_url = urljoin(response.url, product_link)
                yield scrapy.Request(
                    url=product_url,
                    callback=self.parse_product_detail,
                    dont_filter=True
                )
        
        # Paginación
        next_page = response.css('a[rel="next"]::attr(href)').get()
        if not next_page:
            next_page = response.css('.pagination__item--next a::attr(href)').get()
        
        if next_page:
            yield scrapy.Request(
                url=urljoin(response.url, next_page),
                callback=self.parse,
                dont_filter=True
            )

    def extract_variants_from_json(self, response):
        """Extrae variantes desde JSON embebido en scripts"""
        scripts = response.css('script:not([src])::text').getall()
        
        for script in scripts:
            if 'variants' in script and 'price' in script:
                try:
                    # Buscar patrón de producto JSON
                    match = re.search(r'var\s+\w+\s*=\s*({.*?});', script, re.DOTALL)
                    if match:
                        json_str = match.group(1)
                        product_data = json.loads(json_str)
                        
                        if 'variants' in product_data:
                            return product_data['variants']
                except:
                    continue
        
        return []

    def parse_product_detail(self, response):
        product_name = response.css('h1.product__title::text').get()
        if not product_name:
            product_name = response.css('h1::text').get()
        
        if not product_name:
            return
        
        product_name = product_name.strip().upper()
        
        # Extraer variantes
        variants = self.extract_variants_from_json(response)
        
        if variants:
            # Generar un item por cada variante disponible
            for variant in variants:
                if not variant.get('available', True):
                    continue
                
                # Construir nombre con variantes
                variant_title = variant.get('title', '') or variant.get('name', '')
                option1 = variant.get('option1', '')  # Estado Estético
                option2 = variant.get('option2', '')  # Almacenamiento
                option3 = variant.get('option3', '')  # Color (ignorar)
                
                # Precio en centavos
                price_cents = variant.get('price', 0)
                if not price_cents:
                    continue
                
                price = f"${price_cents // 100:,}".replace(',', '.')
                
                # Construir nombre: PRODUCTO - ESTADO - ALMACENAMIENTO
                name_parts = [product_name]
                if option2:  # Almacenamiento
                    name_parts.append(option2.upper())
                if option1:  # Estado Estético
                    name_parts.append(option1.upper())
                
                item = PriceComparisonItem()
                item['name'] = ' - '.join(name_parts)
                item['price'] = price
                yield item
        else:
            # Fallback: producto sin variantes o variantes no detectadas
            price = response.css('.price__sale .price-item--sale::text').get()
            if not price:
                price = response.css('.price__sale::text').get()
            if not price:
                price_elements = response.css('.price:not(.price__regular)::text').getall()
                for p in price_elements:
                    p_clean = p.strip()
                    if '$' in p_clean and 'antes' not in p_clean.lower() and len(p_clean) > 3:
                        price = p_clean
                        break
            
            if price:
                price = price.strip()
                if 'A partir de' in price:
                    price = price.replace('A partir de', '').strip()
                
                item = PriceComparisonItem()
                item['name'] = product_name
                item['price'] = price
                yield item
