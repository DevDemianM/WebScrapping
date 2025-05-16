import scrapy
from price_comparison.items import PriceComparisonItem
import logging
from urllib.parse import urljoin, urlparse, parse_qs


class CeludmovilSpider(scrapy.Spider):
    name = "celudmovil"
    allowed_domains = ["www.celudmovil.com.co"]
    start_urls = [
        "https://www.celudmovil.com.co/collections/all",
        "https://www.celudmovil.com.co/collections/coleccion-de-apple/apple",
        "https://www.celudmovil.com.co/collections/xiaomi",
        "https://www.celudmovil.com.co/collections/samsung",
        "https://www.celudmovil.com.co/collections/experiencia-android/Nokia",
        "https://www.celudmovil.com.co/collections/nuestra-coleccion-celulares-modulaa",
        "https://www.celudmovil.com.co/collections/tablets",
        "https://www.celudmovil.com.co/collections/celulares-oppo",
        "https://www.celudmovil.com.co/collections/adaptadores-y-cables",
        "https://www.celudmovil.com.co/collections/audifonos",
        "https://www.celudmovil.com.co/collections/calidad-en-sonido",
        "https://www.celudmovil.com.co/collections/smartwatch"
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
        products = response.css('div.grid-product__content')
        self.logger.info(f'Encontrados {len(products)} productos en la página {current_page}')

        for product in products:
            item = PriceComparisonItem()
            item['name'] = product.css('div.grid-product__title::text').get(default='').strip()
            item['price'] = product.css('span.sale-price::text').get(default='').strip()
            
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
