import scrapy
from price_comparison.items import PriceComparisonItem
import logging
from urllib.parse import urljoin, urlparse, parse_qs


class PhoneelectricSpider(scrapy.Spider):
    name = "phoneelectric"
    allowed_domains = ["www.phoneelectric.co"]
    start_urls = [
        "https://www.phonelectrics.com/collections/celulares-xiaomi",
        "https://www.phonelectrics.com/collections/xiaomi-redmi",
        "https://www.phonelectrics.com/collections/xiaomi-mi",
        "https://www.phonelectrics.com/collections/xiaomi-pocophone",
        "https://www.phonelectrics.com/collections/celulares-samsung-galaxy",
        "https://www.phonelectrics.com/collections/apple-celulares",
        "https://www.phonelectrics.com/collections/celulares-tecno",
        "https://www.phonelectrics.com/collections/celulares-oppo",
        "https://www.phonelectrics.com/collections/celulares-motorola",
        "https://www.phonelectrics.com/collections/celulares-honor",
        "https://www.phonelectrics.com/collections/celulares-huawei",
        "https://www.phonelectrics.com/collections/celulares-vivo",
        "https://www.phonelectrics.com/collections/celulares-infinix",
        "https://www.phonelectrics.com/collections/celulares-realme",
        "https://www.phonelectrics.com/collections/accesorios-accesorios-xiaomi",
        "https://www.phonelectrics.com/collections/accesorios-realme",
        "https://www.phonelectrics.com/collections/accesorios-accesorios-samsung",
        "https://www.phonelectrics.com/collections/accesorios-accesorios-apple",
        "https://www.phonelectrics.com/collections/accesorios-accesorios-huawei-honor",
        "https://www.phonelectrics.com/collections/apple-ipad",
        "https://www.phonelectrics.com/collections/apple",
        "https://www.phonelectrics.com/collections/bose",
        "https://www.phonelectrics.com/collections/consolas",
        "https://www.phonelectrics.com/collections/accesorios-playstation",
        ""

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
        products = response.css('div.card-wrapper')
        self.logger.info(f'Encontrados {len(products)} productos en la página {current_page}')

        for product in products:
            item = PriceComparisonItem()
            # Extraer nombre del producto
            item['name'] = product.css('h3.card__heading a::text').get(default='').strip()
            
            # Extraer precio de oferta
            sale_price = product.css('span.price-item--sale::text').get(default='').strip()
            if sale_price:
                item['price'] = sale_price
            else:
                # Si no hay precio de oferta, usar el precio regular
                item['price'] = product.css('span.price-item--regular::text').get(default='').strip()
            
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
