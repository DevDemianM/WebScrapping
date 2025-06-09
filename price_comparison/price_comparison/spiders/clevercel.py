import scrapy
import json
from urllib.parse import urljoin, urlparse, parse_qs
from price_comparison.items import PriceComparisonItem
import logging
import re


class ClevercelSpider(scrapy.Spider):
    name = "clevercel"
    allowed_domains = ["www.clevercel.co"]
    start_urls = [
        "https://www.clevercel.co/collections/samsung",
        "https://www.clevercel.co/collections/iphone",
        "https://www.clevercel.co/collections/apple-watch",
        "https://www.clevercel.co/collections/otras-marcas"
    ]

    def parse(self, response):
        """
        Extrae los productos de la página actual y maneja la paginación
        """
        # Obtener la URL base y la colección actual
        parsed_url = urlparse(response.url)
        collection = parsed_url.path.split('/')[-1]
        
        # Obtener la página actual
        query_params = parse_qs(parsed_url.query)
        current_page = int(query_params.get('page', ['1'])[0])
        
        self.logger.info(f'Procesando colección: {collection}, página: {current_page}')

        # Extraer productos de la página actual
        products = response.css('product-item')
        self.logger.info(f'Encontrados {len(products)} productos en la página {current_page}')

        for product in products:
            # Extraer el enlace del producto para ir a su página de detalle
            product_link = product.css('a.product-item-meta__title::attr(href)').get()
            if product_link:
                # Convertir a URL absoluta
                product_url = urljoin(response.url, product_link)
                
                # Extraer información básica desde la página de listado
                basic_info = {
                    'collection': collection,
                    'list_name': product.css('a.product-item-meta__title::text').get(default='').strip(),
                }
                
                # Extraer precio desde la página de listado
                price_text = product.css('span.price--highlight::text').getall()
                if len(price_text) > 1:
                    price_text = price_text[1]
                    if 'Desde' in price_text:
                        price_text = price_text.replace('Desde', '').strip()
                    basic_info['list_price'] = price_text
                else:
                    basic_info['list_price'] = ''

                # Ir a la página de detalle del producto
                yield scrapy.Request(
                    url=product_url,
                    callback=self.parse_product_detail,
                    meta={'basic_info': basic_info},
                    dont_filter=True
                )

        # Construir la URL de la siguiente página
        next_page_number = current_page + 1
        next_page_url = f"{response.url.split('?')[0]}?page={next_page_number}"

        # Verificar si hay más páginas
        if products:  # Si encontramos productos en esta página, intentamos la siguiente
            self.logger.info(f'Intentando acceder a la página {next_page_number} de {collection}')
            yield scrapy.Request(
                url=next_page_url,
                callback=self.parse,
                dont_filter=True
            )
        else:
            self.logger.info(f'No hay más páginas para procesar en la colección {collection}')

    def extract_variant_price_from_json_ld(self, response, category=None, capacity=None):
        """
        Extrae precios específicos de variantes usando JSON-LD (método mejorado)
        """
        try:
            # Buscar JSON-LD
            ld_json = response.xpath('//script[@type="application/ld+json"]/text()').get()
            
            if ld_json:
                data = json.loads(ld_json)
                offers = data.get('offers', [])
                
                for offer in offers:
                    # "name": "Outlet / 128GB / SIERRA BLUE"
                    name_raw = offer.get('name', '')
                    parts = [p.strip() for p in name_raw.split('/')]
                    
                    if len(parts) >= 2:
                        offer_category = parts[0]
                        offer_capacity = parts[1]
                        
                        # Verificar si coincide con los parámetros buscados
                        category_match = not category or category.lower() in offer_category.lower()
                        capacity_match = not capacity or capacity.lower() in offer_capacity.lower()
                        
                        if category_match and capacity_match:
                            # Formatear precio
                            price_val = offer.get('price', 0)
                            try:
                                if isinstance(price_val, str):
                                    price_val = float(price_val.replace(',', '').replace('.', ''))
                                price_str = f"{int(price_val):,}".replace(',', '.')
                                return price_str
                            except (ValueError, TypeError):
                                continue
                                
        except Exception as e:
            self.logger.debug(f"Error extrayendo precio desde JSON-LD: {e}")
        
        return None

    def extract_variant_price(self, response, category=None, capacity=None):
        """
        Extrae el precio específico para una combinación de categoría y capacidad
        """
        # Primero intentar con JSON-LD (método mejorado)
        json_price = self.extract_variant_price_from_json_ld(response, category, capacity)
        if json_price:
            return json_price
        
        # Fallback: método anterior con scripts JS
        try:
            # Buscar script con datos del producto
            product_json = None
            scripts = response.css('script:contains("product"):contains("variants")::text').getall()
            
            for script in scripts:
                if 'variants' in script and 'price' in script:
                    # Buscar el objeto producto en el script
                    product_matches = re.findall(r'product["\s]*:["\s]*({.*?variants.*?})', script, re.DOTALL)
                    for match in product_matches:
                        try:
                            # Limpiar el JSON para que sea válido
                            clean_json = match.replace("'", '"')
                            clean_json = re.sub(r'(\w+):', r'"\1":', clean_json)  # Agregar comillas a las claves
                            product_json = json.loads(clean_json)
                            break
                        except:
                            continue
                    if product_json:
                        break
            
            # Si encontramos datos JSON, buscar la variante específica
            if product_json and 'variants' in product_json:
                for variant in product_json['variants']:
                    # Verificar si la variante coincide con los parámetros
                    variant_options = str(variant.get('options', [])).lower()
                    variant_title = str(variant.get('title', '')).lower()
                    
                    match_category = not category or category.lower() in variant_title or category.lower() in variant_options
                    match_capacity = not capacity or capacity.lower() in variant_title or capacity.lower() in variant_options
                    
                    if match_category and match_capacity:
                        # Obtener precio en centavos y convertir
                        price_cents = variant.get('price', 0)
                        if price_cents:
                            price_formatted = f"{price_cents // 100:,.0f}".replace(',', '.')
                            if price_cents % 100:
                                price_formatted += f".{price_cents % 100:02d}"
                            return price_formatted
                            
        except Exception as e:
            self.logger.debug(f"Error extrayendo precio JSON: {e}")
        
        # Fallback final: buscar precios en el HTML
        main_price = response.css('span.price.price--highlight.price--large::text').get(default='').strip()
        if not main_price:
            main_price = response.css('.price--highlight::text').get(default='').strip()
        if not main_price:
            main_price = response.css('span.price--highlight::text').get(default='').strip()
        if not main_price:
            # Buscar precio en el texto "Precio de venta"
            main_price = response.css('span:contains("Precio de venta") + *::text').get(default='').strip()
        if not main_price:
            # Extraer precio del patrón $X.XXX.XXX
            price_pattern = re.search(r'\$[\d,\.]+', response.text)
            main_price = price_pattern.group(0) if price_pattern else ''
        
        # Limpiar el precio
        if main_price and 'Desde' in main_price:
            main_price = main_price.replace('Desde', '').strip()
            
        return main_price

    def get_all_variants_from_json_ld(self, response):
        """
        Extrae todas las variantes disponibles desde JSON-LD
        """
        try:
            ld_json = response.xpath('//script[@type="application/ld+json"]/text()').get()
            
            if ld_json:
                data = json.loads(ld_json)
                offers = data.get('offers', [])
                
                categories = set()
                capacities = set()
                
                for offer in offers:
                    name_raw = offer.get('name', '')
                    parts = [p.strip() for p in name_raw.split('/')]
                    
                    if len(parts) >= 2:
                        categories.add(parts[0])
                        # Validar que sea almacenamiento real
                        storage = parts[1]
                        storage_patterns = ['128GB', '256GB', '512GB', '1TB', '1024GB', '64GB', '32GB']
                        if any(pattern.upper() in storage.upper() for pattern in storage_patterns):
                            capacities.add(storage)
                
                return list(categories), list(capacities)
                
        except Exception as e:
            self.logger.debug(f"Error extrayendo variantes desde JSON-LD: {e}")
        
        return [], []

    def parse_product_detail(self, response):
        """
        Extrae información detallada del producto desde su página individual
        """
        basic_info = response.meta['basic_info']
        
        # Extraer nombre completo del producto
        product_name = response.css('h1.product-meta__title::text').get()
        if not product_name:
            product_name = response.css('h1::text').get()
        if not product_name:
            product_name = basic_info['list_name']
        
        product_name = product_name.strip() if product_name else ''

        # Extraer marca
        brand = response.css('span.product__vendor::text').get(default='').strip()
        if not brand:
            # Intentar extraer marca del nombre del producto
            brand_match = re.match(r'^([A-Za-z]+)', product_name)
            brand = brand_match.group(1) if brand_match else ''

        # Primero intentar extraer variantes desde JSON-LD
        json_categories, json_capacities = self.get_all_variants_from_json_ld(response)
        
        # Si JSON-LD tiene datos, usarlos
        if json_categories or json_capacities:
            category_options = json_categories
            capacity_options = json_capacities
            self.logger.info(f'Variantes desde JSON-LD - Categorías: {category_options}, Capacidades: {capacity_options}')
        else:
            # Fallback: método anterior con selectores HTML
            # Extraer todas las variantes disponibles (categorías y capacidades)
            category_options = []
            
            # Buscar selectores de categoría
            category_selectors = [
                'input[name="Categoría"] + label::text',
                'label[for*="categoría"]::text',
                'label[for*="Categoría"]::text',
                '.product-form__option-value[data-option-name="Categoría"]::text'
            ]
            
            for selector in category_selectors:
                found_categories = response.css(selector).getall()
                if found_categories:
                    category_options = [cat.strip() for cat in found_categories if cat.strip()]
                    break
            
            # Si no encuentra con selectors, buscar en texto
            if not category_options:
                category_keywords = ['Outlet', 'Semi Nuevo', 'Como Nuevo', 'Nuevo']
                for keyword in category_keywords:
                    if keyword.lower() in response.text.lower():
                        category_options.append(keyword)
            
            # Obtener opciones de capacidad (solo almacenamiento real)
            capacity_options = []
            
            # Buscar selectores de capacidad
            capacity_selectors = [
                'input[name="Capacidad"] + label::text',
                'label[for*="capacidad"]::text',
                'label[for*="Capacidad"]::text',
                '.product-form__option-value[data-option-name="Capacidad"]::text'
            ]
            
            for selector in capacity_selectors:
                found_capacities = response.css(selector).getall()
                if found_capacities:
                    capacity_options = [cap.strip() for cap in found_capacities if cap.strip()]
                    break
            
            # Si no encuentra con selectors, buscar en texto (solo almacenamiento real)
            if not capacity_options:
                capacity_pattern = re.findall(r'\b(128GB|256GB|512GB|1TB|1024GB|64GB|32GB)\b', response.text, re.IGNORECASE)
                capacity_options = list(set(capacity_pattern)) if capacity_pattern else []

        # Limpiar y validar opciones
        category_options = [cat.strip() for cat in category_options if cat.strip()]
        capacity_options = [cap.strip() for cap in capacity_options if cap.strip()]

        # Si no hay variantes específicas, crear un item con la información base
        if not category_options and not capacity_options:
            price = self.extract_variant_price(response)
            if price:
                item = PriceComparisonItem()
                item['name'] = f"{product_name.upper()} - {basic_info['collection'].upper()}"
                item['price'] = price
                yield item
        else:
            # Crear items para cada combinación de categoría y capacidad
            if not category_options:
                category_options = ['']
            if not capacity_options:
                capacity_options = ['']
                
            for category in category_options:
                for capacity in capacity_options:
                    # Extraer precio específico para esta combinación
                    specific_price = self.extract_variant_price(response, category, capacity)
                    
                    if specific_price:
                        item = PriceComparisonItem()
                        
                        # Construir nombre descriptivo en mayúsculas
                        name_parts = [product_name.upper()]
                        if capacity:
                            name_parts.append(capacity.upper())
                        if category:
                            name_parts.append(category.upper())
                        name_parts.append(basic_info['collection'].upper())
                        
                        item['name'] = ' - '.join(name_parts)
                        item['price'] = specific_price
                        
                        yield item

        self.logger.info(f'Producto procesado: {product_name}')
        self.logger.info(f'  - Categorías encontradas: {category_options}')
        self.logger.info(f'  - Capacidades encontradas: {capacity_options}')
        self.logger.info(f'  - Total items generados: {len(category_options or [""])} * {len(capacity_options or [""])} = {len(category_options or [""]) * len(capacity_options or [""])}')
