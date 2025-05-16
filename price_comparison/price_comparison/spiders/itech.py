import scrapy
from price_comparison.items import PriceComparisonItem
import logging
from urllib.parse import urljoin, urlparse, parse_qs


class ItechSpider(scrapy.Spider):
    name = "itech"
    allowed_domains = ["itechcolombia.co"]
    start_urls = [
        "https://itechcolombia.co/product-category/apple/?orderby=date",
        "https://itechcolombia.co/product-category/samsung/?orderby=date",
        "https://itechcolombia.co/product-category/playstation/?orderby=date",
        "https://itechcolombia.co/product-category/xiaomi/?orderby=date",
        "https://itechcolombia.co/shop/"
    ]

    def __init__(self, *args, **kwargs):
        super(ItechSpider, self).__init__(*args, **kwargs)
        self.processed_products = set()  # Conjunto para almacenar productos ya procesados

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
        products = response.css('li.product')
        self.logger.info(f'Encontrados {len(products)} productos en la página {current_page}')

        # Contador para productos nuevos en esta página
        new_products_count = 0

        for product in products:
            item = PriceComparisonItem()
            name = product.css('h2.woocommerce-loop-product__title a::text').get(default='').strip()
            price = product.css('span.woocommerce-Price-amount bdi::text').get(default='').strip()
            
            # Crear un identificador único para el producto
            product_id = f"{name}_{price}"
            
            # Verificar si el producto ya fue procesado
            if product_id not in self.processed_products:
                self.processed_products.add(product_id)
                item['name'] = name
                item['price'] = price
                new_products_count += 1
                yield item

        self.logger.info(f'Productos nuevos encontrados en la página {current_page}: {new_products_count}')

        # Si no encontramos productos nuevos en esta página, detenemos la paginación
        if new_products_count == 0:
            self.logger.info(f'No se encontraron productos nuevos en la página {current_page} de {collection}. Finalizando paginación.')
            return

        # Construir la URL de la siguiente página
        next_page_number = current_page + 1
        next_page_url = f"{response.url.split('?')[0]}?page={next_page_number}"

        # Intentar acceder a la siguiente página
        self.logger.info(f'Intentando acceder a la página {next_page_number} de {collection}')
        yield scrapy.Request(
            url=next_page_url,
            callback=self.parse,
            dont_filter=True
        )
