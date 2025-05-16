import scrapy
from price_comparison.items import PriceComparisonItem
import logging
from urllib.parse import urljoin, urlparse, parse_qs


class ClevercelSpider(scrapy.Spider):
    name = "clevercel"
    allowed_domains = ["www.clevercel.com.co"]
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
            item = PriceComparisonItem()
            item['name'] = product.css('a.product-item-meta__title::text').get(default='').strip()
            item['price'] = product.css('span.price--highlight::text').get(default='').strip()
            
            yield item

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
