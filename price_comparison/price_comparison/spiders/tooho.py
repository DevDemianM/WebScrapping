import scrapy
from price_comparison.items import PriceComparisonItem
import logging
from urllib.parse import urljoin, urlparse, parse_qs


class ToohoSpider(scrapy.Spider):
    name = "tooho"
    allowed_domains = ["www.tohoo.store"]
    start_urls = [
        "https://www.tohoo.store/Celulares",
        "https://www.tohoo.store/Celulares/apple",
        "https://www.tohoo.store/Celulares/samsung",
        "https://www.tohoo.store/Celulares/xiaomi",
        "https://www.tohoo.store/relojes",
        "https://www.tohoo.store/computadores-y-tablets",
        "https://www.tohoo.store/audio",
        "https://www.tohoo.store/accesorios"
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
        products = response.css('div.vtex-search-result-3-x-galleryItem')
        self.logger.info(f'Encontrados {len(products)} productos en la página {current_page}')

        for product in products:
            item = PriceComparisonItem()
            product_name = product.css('span.vtex-product-summary-2-x-productBrand.vtex-product-summary-2-x-brandName.t-body::text').get(default='').strip()
            item['name'] = f"{product_name.upper()} - {collection.upper()}"
            price_parts = product.css('span.vtex-product-price-1-x-currencyContainer span::text').getall()
            item['price'] = ''.join([p.strip() for p in price_parts])
            
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
