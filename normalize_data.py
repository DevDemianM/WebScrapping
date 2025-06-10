import json
import re
import os
from datetime import datetime

class DataNormalizer:
    def __init__(self):
        # Diccionario de mapeo de marcas
        self.brand_mapping = {
            'IPHONE': 'APPLE',
            'POCO': 'XIAOMI',
            'REDMI': 'XIAOMI',
            'MI': 'XIAOMI',
            'POCOPHONE': 'XIAOMI',
            'GALAXY': 'SAMSUNG',
            'HONOR': 'HUAWEI',
            'REALME': 'OPPO',
            'ONEPLUS': 'OPPO',
            'IQOO': 'VIVO',
            'NOTHING': 'NOTHING',
            'MOTOROLA': 'MOTOROLA',
            'HUAWEI': 'HUAWEI',
            'TECNO': 'TECNO',
            'INFINIX': 'INFINIX',
            'OPPO': 'OPPO',
            'VIVO': 'VIVO',
            'NOKIA': 'NOKIA',
            'BLACKBERRY': 'BLACKBERRY',
            'LG': 'LG',
            'SONY': 'SONY',
            'ALCATEL': 'ALCATEL',
            'TCL': 'TCL',
            'LENOVO': 'LENOVO'
        }
        
        # Diccionario para productos que no tienen marca explícita pero sabemos cuál es
        self.implicit_brands = {
            'AIRPODS': 'APPLE',
            'IPAD': 'APPLE', 
            'MACBOOK': 'APPLE',
            'IMAC': 'APPLE',
            'IWATCH': 'APPLE',
            'WATCH': 'APPLE',  # Para Apple Watch
            'PLAYSTATION': 'SONY',
            'PS5': 'SONY',
            'PS4': 'SONY',
            'XBOX': 'MICROSOFT',
            'SURFACE': 'MICROSOFT'
        }
        
        # Patrones para detectar marcas dentro del texto del producto
        self.brand_patterns = {
            'APPLE': ['APPLE', 'IPHONE', 'IPAD', 'MACBOOK', 'AIRPODS', 'IMAC', 'WATCH SERIES', 'WATCH ULTRA'],
            'SAMSUNG': ['SAMSUNG', 'GALAXY'],
            'XIAOMI': ['XIAOMI', 'REDMI', 'POCO', 'MI '],
            'HUAWEI': ['HUAWEI', 'HONOR'],
            'SONY': ['SONY', 'PLAYSTATION', 'PS5', 'PS4'],
            'NINTENDO': ['NINTENDO', 'SWITCH'],
            'JBL': ['JBL'],
            'BOSE': ['BOSE'],
            'MICROSOFT': ['MICROSOFT', 'XBOX', 'SURFACE'],
            'MOTOROLA': ['MOTOROLA', 'MOTO'],
            'OPPO': ['OPPO', 'REALME', 'ONEPLUS'],
            'VIVO': ['VIVO', 'IQOO'],
            'TECNO': ['TECNO'],
            'INFINIX': ['INFINIX'],
            'LENOVO': ['LENOVO'],
            'NOTHING': ['NOTHING'],
            'NOKIA': ['NOKIA'],
            'LG': ['LG'],
            'TCL': ['TCL'],
            'ALCATEL': ['ALCATEL']
        }
        
        # Diccionario de capacidades normalizadas
        self.capacity_mapping = {
            '1024GB': '1TB',
            '2048GB': '2TB',
            '4096GB': '4TB',
            '512MB': '0.5GB',
            '1024MB': '1GB',
            '2048MB': '2GB',
            '4096MB': '4GB',
            '8192MB': '8GB',
            '1TERA': '1TB'
        }
        
        # Diccionario de condiciones normalizadas (en orden de prioridad)
        self.condition_mapping = {
            'OUTLET': 'USADO',
            'USADO': 'USADO',
            'COMO NUEVO': 'COMO NUEVO',
            'SEMINUEVO': 'SEMINUEVO',
            'SEMI NUEVO': 'SEMINUEVO',
            'EXH': 'SEMINUEVO',
            'EXH PREMIUM': 'SEMINUEVO',
            'DE EXH': 'SEMINUEVO',
            'DE EXH PREMIUM': 'SEMINUEVO',
            'CPO': 'SEMINUEVO',
            'PREMIUM': 'SEMINUEVO',
            'NUEVO': 'NUEVO',
            'REFURBISHED': 'SEMINUEVO',
            'REACONDICIONADO': 'SEMINUEVO',
            'OPEN BOX': 'SEMINUEVO'
        }
        
        # Diccionario de tipos de SIM normalizados
        self.sim_type_mapping = {
            'E-SIM': 'SIM VIRTUAL',
            'ESIM': 'SIM VIRTUAL',
            'SIM VIRTUAL': 'SIM VIRTUAL',
            'S-FIS': 'SIM FISICA',
            'SIM FISICA': 'SIM FISICA',
            'SIM FÍSICO': 'SIM FISICA',
            'DUAL SIM FISICA': 'SIM FISICA',
            'DUAL SIM': 'SIM FISICA'
        }
        
        # Palabras a eliminar del nombre del producto
        self.words_to_remove = [
            'CELULAR', 'CELULARES', 'OTRAS MARCAS', 'ALL', 'DE', 'LA', 'EL', 'Y',
            '5G', '4G', 'LTE', 'WIFI', 'CELLULAR', 'GPS', 'PREVENTA',
            'NEGRO', 'BLANCO', 'AZUL', 'ROJO', 'VERDE', 'AMARILLO', 'MORADO', 'ROSADO',
            'ROSA', 'DORADO', 'GRIS', 'PLATEADO', 'TITANIUM', 'NATURAL', 'DESERT',
            'MIDNIGHT', 'STARLIGHT', 'PURPLE', 'BLUE', 'RED', 'GREEN', 'YELLOW',
            'PINK', 'GOLD', 'SILVER', 'SPACE', 'GRAY', 'GREY', 'LILA', 'GRAPHITE',
            'ORIGINAL', 'GARANTIA', 'SELLADO', 'OFERTA', 'PROMOCION', 'ESPECIAL'
        ]
        
        # Orden de prioridad para condiciones (de mayor a menor prioridad)
        self.condition_priority = ['USADO', 'COMO NUEVO', 'SEMINUEVO', 'NUEVO']

    def remove_accents(self, text):
        """Elimina tildes y caracteres especiales"""
        import unicodedata
        return ''.join(c for c in unicodedata.normalize('NFD', text)
                      if unicodedata.category(c) != 'Mn')

    def detect_brand_from_product_name(self, product_name):
        """Detecta la marca a partir del nombre del producto"""
        product_upper = product_name.upper()
        
        # Buscar patrones de marca en el texto
        for brand, patterns in self.brand_patterns.items():
            for pattern in patterns:
                if pattern in product_upper:
                    return brand
        
        # Buscar marcas implícitas (productos que sabemos de qué marca son)
        for product_key, brand in self.implicit_brands.items():
            if product_key in product_upper:
                return brand
                
        return None

    def is_mobile_device(self, name):
        """Detecta si es un dispositivo móvil que usa SIM"""
        if not name:
            return False
            
        name_upper = name.upper()
        
        # Palabras que indican que ES un celular/móvil
        mobile_keywords = [
            'IPHONE', 'GALAXY', 'REDMI', 'POCO', 'XIAOMI', 'HUAWEI', 'HONOR',
            'MOTOROLA', 'MOTO', 'OPPO', 'REALME', 'ONEPLUS', 'VIVO', 'IQOO',
            'NOKIA', 'TECNO', 'INFINIX', 'NOTHING', 'BLACKBERRY', 'LG',
            'CELULAR', 'SMARTPHONE', 'TELEFONO', 'MOVIL'
        ]
        
        # Palabras que indican que NO es un celular
        non_mobile_keywords = [
            'AIRPODS', 'AUDIFONOS', 'EARBUDS', 'HEADPHONES', 'BUDS',
            'WATCH', 'SMARTWATCH', 'RELOJ', 'RELOJES',
            'IPAD', 'TABLET', 'TAB',
            'MACBOOK', 'LAPTOP', 'NOTEBOOK', 'COMPUTER',
            'CARGADOR', 'CHARGER', 'CABLE', 'CUBO',
            'MOUSE', 'TECLADO', 'KEYBOARD',
            'ACCESORIOS', 'ACCESORIO', 'FUNDA', 'CASE',
            'PROTECTOR', 'VIDRIO', 'SCREEN',
            'SPEAKER', 'PARLANTE', 'BOCINA',
            'POWERBANK', 'BATERIA',
            'CONSOLA', 'PLAYSTATION', 'PS4', 'PS5', 'XBOX', 'NINTENDO',
            'PENCIL', 'STYLUS'
        ]
        
        # Primero verificar si contiene palabras que definitivamente NO son móviles
        for keyword in non_mobile_keywords:
            if keyword in name_upper:
                return False
        
        # Luego verificar si contiene palabras que SÍ son móviles
        for keyword in mobile_keywords:
            if keyword in name_upper:
                return True
                
        return False

    def extract_sim_type(self, name):
        """Extrae y normaliza el tipo de SIM SOLO para dispositivos móviles"""
        if not name:
            return "", name
        
        # Solo extraer SIM si es un dispositivo móvil
        if not self.is_mobile_device(name):
            return "", name
        
        name_upper = name.upper()
        
        # Buscar patrones de SIM más específicos
        sim_patterns = {
            'SIM VIRTUAL': ['E-SIM', 'ESIM', 'SIM VIRTUAL', 'VIRTUAL'],
            'SIM FISICA': ['SIM FISICA', 'SIM FÍSICO', 'S-FIS', 'SFIS', 'FISICA', 'FÍSICO'],
            'DUAL SIM': ['DUAL SIM']
        }
        
        for sim_type, patterns in sim_patterns.items():
            for pattern in patterns:
                if pattern in name_upper:
                    # Remover el patrón del nombre
                    cleaned_name = re.sub(rf'\b{re.escape(pattern)}\b', '', name, flags=re.IGNORECASE)
                    cleaned_name = re.sub(r'\s+', ' ', cleaned_name).strip()
                    return sim_type, cleaned_name
        
        # Si es un dispositivo móvil pero no especifica SIM, usar SIM FISICA por defecto
        return "SIM FISICA", name

    def extract_condition_with_priority(self, name):
        """Extrae condición con prioridad y elimina duplicaciones"""
        if not name:
            return "", name
        
        # Mapeo de condiciones con prioridad (mayor número = mayor prioridad)
        condition_priority = {
            'USADO': 4,      # EXH y OUTLET también se convierten a USADO
            'COMO NUEVO': 3, 
            'SEMINUEVO': 2,
            'SEMI NUEVO': 2,
            'NUEVO': 1
        }
        
        # Patrones más específicos primero - ORDEN IMPORTANTE
        condition_patterns = [
            (r'\b(COMO\s+NUEVO)\b', 'COMO NUEVO'),
            (r'\b(SEMI\s*NUEVO)\b', 'SEMINUEVO'),
            (r'\b(SEMINUEVO)\b', 'SEMINUEVO'),
            (r'\b(USADO)\b', 'USADO'),           # EXH ya se convirtió a USADO
            (r'\b(OUTLET)\b', 'USADO'),         # OUTLET = USADO
            (r'\b(NUEVO)\s+DUAL\b', 'NUEVO'),   # NUEVO DUAL -> NUEVO
            (r'\b(NUEVO)\b', 'NUEVO')
        ]
        
        found_conditions = []
        cleaned_name = name
        
        # Buscar todas las condiciones y removerlas
        for pattern, condition in condition_patterns:
            matches = list(re.finditer(pattern, cleaned_name, re.IGNORECASE))
            for match in matches:
                found_conditions.append(condition)
            # Remover TODAS las ocurrencias del patrón
            cleaned_name = re.sub(pattern, '', cleaned_name, flags=re.IGNORECASE)
        
        # Eliminar "DUAL" suelto cuando ya hay "NUEVO"
        if 'NUEVO' in found_conditions:
            cleaned_name = re.sub(r'\bDUAL\b', '', cleaned_name, flags=re.IGNORECASE)
        
        # Limpiar espacios múltiples y separadores
        cleaned_name = re.sub(r'\s+', ' ', cleaned_name).strip()
        cleaned_name = re.sub(r'\s*-\s*', ' - ', cleaned_name)
        cleaned_name = re.sub(r'^[\s\-]+|[\s\-]+$', '', cleaned_name)
        
        if not found_conditions:
            return "NUEVO", cleaned_name  # Por defecto NUEVO
        
        # Obtener la condición con mayor prioridad (eliminar duplicados)
        unique_conditions = list(set(found_conditions))
        best_condition = max(unique_conditions, key=lambda x: condition_priority.get(x, 0))
        
        return best_condition, cleaned_name

    def clean_unwanted_words(self, name):
        """Limpia palabras y patrones no deseados del nombre del producto"""
        if not name:
            return name
        
        # Lista de palabras a eliminar completamente
        words_to_remove = [
            'CELULARES', 'ALL', 'DE', 'GADGETS', 'ACCESORIOS', 'ACCESORIO',
            'ELECTRONICA', 'TECNOLOGIA', 'TECH'
        ]
        
        # PATRONES ESPECÍFICOS MUY IMPORTANTES - Ejecutar PRIMERO
        
        # 1. Eliminar "OTRAS MARCAS" o "OTRAS - MARCAS" COMPLETAMENTE
        name = re.sub(r'\b(OTRAS\s*-?\s*MARCAS?)\b', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\b(OTRAS)\s*-\s*(MARCAS?)\b', '', name, flags=re.IGNORECASE)
        
        # 2. Eliminar "AUDIFONOS" SOLO cuando aparece con AIRPODS
        if 'AIRPODS' in name.upper():
            name = re.sub(r'\b(AUDIFONOS)\b', '', name, flags=re.IGNORECASE)
        
        # 3. Eliminar "CELULAR" cuando aparece con IPHONE
        if 'IPHONE' in name.upper():
            name = re.sub(r'\b(CELULAR)\b', '', name, flags=re.IGNORECASE)
        
        # 4. Eliminar patrones técnicos generales
        
        # Eliminar patrones de RED (4G, 5G, LTE, etc.)
        name = re.sub(r'\b(4G|5G|LTE|3G|2G)\+?\b', '', name, flags=re.IGNORECASE)
        
        # Eliminar patrones de RAM (SOLO números de 1 dígito: 4+, 8+, 6+, etc.)
        # NO eliminar almacenamiento válido como 128+, 256+, etc.
        name = re.sub(r'\b([1-9])\+\s*(GB)?\b', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\b([1-9])\s*\+\b', '', name, flags=re.IGNORECASE)
        
        # Eliminar patrones de SIM (S-FIS, E-SIM, etc.) ya que se maneja por separado
        name = re.sub(r'\b(S\s*-?\s*FIS)\b', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\b(E\s*-?\s*SIM)\b', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\b(SFIS|ESIM)\b', '', name, flags=re.IGNORECASE)
        
        # Eliminar años entre paréntesis (2020), (2022), etc.
        name = re.sub(r'\s*\((\d{4})\)\s*', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\s*\(\s*(\d{4})\s*\)\s*', '', name, flags=re.IGNORECASE)
        
        # Eliminar colores sueltos que quedan después de limpiar patrones técnicos
        colors_to_remove = ['BLANCO', 'NEGRO', 'AZUL', 'ROJO', 'VERDE', 'AMARILLO', 'MORADO', 'ROSADO', 'ROSA', 'DORADO', 'GRIS', 'PLATEADO']
        for color in colors_to_remove:
            # Solo eliminar si está solo (no como parte de un nombre de producto)
            name = re.sub(rf'\b{color}\b(?!\s+\w)', '', name, flags=re.IGNORECASE)
        
        # Eliminar "+6" solo si es un celular/dispositivo móvil
        if self.is_mobile_device(name):
            name = re.sub(r'\+\s*6\b', '', name, flags=re.IGNORECASE)
        
        # Limpiar patrones EXH PRIMERO (antes de extraer condiciones)
        name = re.sub(r'\bEXH\s*PREMIUM\b', 'USADO', name, flags=re.IGNORECASE)
        name = re.sub(r'\bEXH\b', 'USADO', name, flags=re.IGNORECASE)
        
        # Eliminar palabras no deseadas generales
        for word in words_to_remove:
            name = re.sub(rf'\b{re.escape(word)}\b', '', name, flags=re.IGNORECASE)
        
        # Limpiar espacios múltiples y separadores
        name = re.sub(r'\s+', ' ', name).strip()
        name = re.sub(r'\s*-\s*', ' - ', name)
        
        return name

    def remove_brand_duplication(self, name, brand):
        """Elimina duplicaciones de la marca en el nombre de forma más inteligente"""
        if not name or not brand or brand == 'UNKNOWN':
            return name
        
        name_upper = name.upper()
        brand_upper = brand.upper()
        
        # Casos especiales para APPLE
        if brand_upper == 'APPLE':
            # Para productos Apple iPhone, eliminar duplicaciones de APPLE E IPHONE
            if 'IPHONE' in name_upper:
                # Eliminar TODAS las instancias de APPLE del nombre
                name_clean = re.sub(r'\bAPPLE\b', '', name_upper, flags=re.IGNORECASE)
                # Contar cuántas veces aparece IPHONE
                iphone_count = name_clean.count('IPHONE')
                if iphone_count > 1:
                    # Si hay múltiples IPHONE, reemplazar todos con uno solo
                    name_clean = re.sub(r'\bIPHONE\b', '###IPHONE###', name_clean)
                    name_clean = name_clean.replace('###IPHONE###', 'IPHONE', 1)
                    name_clean = name_clean.replace('###IPHONE###', '')
                name_clean = re.sub(r'\s+', ' ', name_clean).strip()
                return name_clean
            # Para otros productos Apple (AirPods, iPad), eliminar duplicaciones de APPLE
            else:
                name_clean = re.sub(r'\bAPPLE\b', '', name_upper, flags=re.IGNORECASE)
                name_clean = re.sub(r'\s+', ' ', name_clean).strip()
                return name_clean
        
        # Para otras marcas, eliminar duplicaciones normalmente
        brand_count = name_upper.count(brand_upper)
        
        if brand_count > 0:
            name_clean = re.sub(rf'\b{re.escape(brand_upper)}\b', '', name_upper, flags=re.IGNORECASE)
            name_clean = re.sub(r'\s+', ' ', name_clean).strip()
            return name_clean
        
        return name

    def normalize_brand(self, brand, product_name=None):
        """Normaliza la marca, detectando desde el nombre del producto si es necesario"""
        if not brand or brand.upper() == 'UNKNOWN':
            if product_name:
                detected_brand = self.detect_brand_from_product_name(product_name)
                if detected_brand:
                    return detected_brand
            return None  # Cambio: retornar None en lugar de 'UNKNOWN'
        
        brand_upper = brand.upper()
        return self.brand_mapping.get(brand_upper, brand_upper)

    def extract_capacity_from_name(self, name):
        """Extrae SOLO almacenamiento real del nombre del producto, ignorando RAM"""
        if not name:
            return "", name
        
        # Patrones SOLO para almacenamiento real (NO RAM)
        storage_patterns = [
            r'\b(128GB)\b',
            r'\b(256GB)\b', 
            r'\b(512GB)\b',
            r'\b(1TB)\b',
            r'\b(1024GB)\b',  # Convertir a 1TB
            r'\b(2TB)\b',
            r'\b(2048GB)\b'   # Convertir a 2TB
        ]
        
        # Patrones de RAM que debemos ELIMINAR del nombre pero NO usar como capacidad
        ram_patterns_to_remove = [
            r'\b3GB\b',
            r'\b4GB\b',
            r'\b6GB\b',
            r'\b8GB\b',
            r'\b12GB\b',
            r'\b16GB\b',
            r'\b32GB\b',  # También puede ser RAM en algunos casos
            r'\b64GB\b'   # También puede ser RAM en algunos casos
        ]
        
        # Buscar SOLO almacenamiento real
        storage_matches = []
        for pattern in storage_patterns:
            matches = re.findall(pattern, name, re.IGNORECASE)
            storage_matches.extend(matches)
        
        # Limpiar el nombre eliminando TODA la RAM y capacidades
        cleaned_name = name
        for pattern in storage_patterns + ram_patterns_to_remove:
            cleaned_name = re.sub(pattern, '', cleaned_name, flags=re.IGNORECASE)
        
        cleaned_name = re.sub(r'\s+', ' ', cleaned_name).strip()
        
        # Si encontramos almacenamiento real, usar eso
        if storage_matches:
            # Tomar el último (más probable que sea el almacenamiento principal)
            storage = storage_matches[-1].upper()
            normalized_capacity = self.normalize_capacity(storage)
            return normalized_capacity, cleaned_name
        
        # Si NO hay almacenamiento real, devolver sin capacidad
        return "", cleaned_name

    def normalize_capacity(self, capacity):
        """Normaliza la capacidad de almacenamiento"""
        if not capacity:
            return ""
        
        capacity = capacity.upper().strip()
        return self.capacity_mapping.get(capacity, capacity)

    def clean_multiple_separators(self, text):
        """Limpia guiones múltiples y espacios de forma más agresiva"""
        if not text:
            return text
        
        # Reemplazar múltiples guiones consecutivos
        text = re.sub(r'-{2,}', '-', text)
        
        # Reemplazar patrones como "- -" o "- - -" con un solo guión
        text = re.sub(r'(\s*-\s*){2,}', ' - ', text)
        
        # Limpiar espacios múltiples
        text = re.sub(r'\s{2,}', ' ', text)
        
        # Limpiar guiones al inicio y final
        text = re.sub(r'^[\s\-]+|[\s\-]+$', '', text)
        
        # Dividir por guiones, limpiar partes vacías y reconstruir
        parts = text.split(' - ')
        clean_parts = []
        
        for part in parts:
            part = part.strip()
            if part and part != '-' and len(part) > 0:
                clean_parts.append(part)
        
        return ' - '.join(clean_parts)

    def normalize_product(self, name, brand, price, store, url):
        """Normaliza un producto completo con mejor detección y sin duplicaciones"""
        if not name:
            return None
        
        # Limpiar el nombre inicial
        original_name = name
        cleaned_name = self.clean_name(name)
        
        # Extraer información del producto
        brand_info = self.extract_brand(cleaned_name, brand)
        condition, name_after_condition = self.extract_condition_with_priority(cleaned_name)
        
        # SIM type solo para dispositivos móviles
        sim_type, name_after_sim = self.extract_sim_type(name_after_condition)
        
        # Capacidad de almacenamiento
        storage_capacity, name_after_storage = self.extract_storage_capacity(name_after_sim)
        
        # Limpiar nombre final
        final_name = self.clean_final_name(name_after_storage, brand_info)
        
        # Construir el nombre normalizado SIN DUPLICACIONES
        parts = []
        
        if brand_info:
            parts.append(brand_info)
        
        if final_name:
            parts.append(final_name)
        
        # Solo agregar SIM si es un dispositivo móvil
        if sim_type:
            parts.append(sim_type)
        
        # Solo agregar condición una vez
        if condition:
            parts.append(condition)
        
        if storage_capacity:
            parts.append(storage_capacity)
        
        normalized_name = ' - '.join(parts)
        
        # Validación final: eliminar duplicaciones que puedan quedar
        normalized_name = self.remove_final_duplications(normalized_name)
        
        # Validar que el producto tenga información mínima
        if not normalized_name or len(normalized_name.strip()) < 3:
            return None
        
        return {
            'normalized_name': normalized_name,
            'original_name': original_name,
            'brand': brand_info,
            'condition': condition,
            'sim_type': sim_type if sim_type else None,
            'storage_capacity': storage_capacity,
            'price': price,
            'url': url
        }

    def remove_final_duplications(self, text):
        """Elimina duplicaciones finales en el texto normalizado"""
        if not text:
            return text
        
        parts = text.split(' - ')
        seen = set()
        clean_parts = []
        
        for part in parts:
            part = part.strip()
            if part and part not in seen:
                seen.add(part)
                clean_parts.append(part)
        
        return ' - '.join(clean_parts)

    def normalize_store_data(self, input_file, output_file):
        """Normaliza los datos de una tienda específica, manejando múltiples arrays JSON"""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extraer todos los arrays JSON del contenido
            arrays = []
            depth_level = 0
            start_idx = -1
            
            for i, char in enumerate(content):
                if char == '[':
                    if depth_level == 0:
                        start_idx = i
                    depth_level += 1
                elif char == ']':
                    depth_level -= 1
                    if depth_level == 0 and start_idx != -1:
                        # Extraer el array completo
                        array_content = content[start_idx:i + 1]
                        arrays.append(array_content)
                        start_idx = -1
            
            if not arrays:
                print(f"⚠️ No se encontraron arrays JSON en {input_file}")
                return 0
            
            # Parsear y combinar todos los arrays
            all_products = []
            for j, array_str in enumerate(arrays):
                try:
                    array_data = json.loads(array_str)
                    if isinstance(array_data, list):
                        all_products.extend(array_data)
                    else:
                        all_products.append(array_data)
                except json.JSONDecodeError as e:
                    print(f"⚠️ Error parseando array {j+1} en {input_file}: {e}")
                    continue
            
            if not all_products:
                print(f"⚠️ No se pudieron extraer productos de {input_file}")
                return 0
            
            # Normalizar todos los productos
            normalized_data = []
            for product in all_products:
                # Extraer campos con valores por defecto seguros
                name = product.get('name', '')
                price = product.get('price', '0')
                brand = product.get('brand', '')  # Campo que puede no existir
                store = product.get('store', '')  # Campo que puede no existir  
                url = product.get('url', '')      # Campo que puede no existir
                
                normalized_product = self.normalize_product(name, brand, price, store, url)
                if normalized_product:  # Solo agregar si la normalización fue exitosa
                    normalized_data.append(normalized_product)
            
            # Crear directorio de salida si no existe
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(normalized_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Normalizado {input_file} → {output_file} ({len(normalized_data)} productos)")
            return len(normalized_data)
            
        except Exception as e:
            print(f"❌ Error procesando {input_file}: {str(e)}")
            return 0

    def clean_name(self, name):
        """Limpia el nombre inicial del producto"""
        if not name:
            return ""
        
        # Remover tildes y convertir a mayúsculas
        cleaned = self.remove_accents(name).upper()
        
        # Limpiar EXH ANTES de otras operaciones
        cleaned = re.sub(r'\bEXH\s*PREMIUM\b', 'USADO', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\bEXH\b', 'USADO', cleaned, flags=re.IGNORECASE)
        
        # Limpiar espacios múltiples
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned

    def extract_brand(self, name, brand_hint=""):
        """Extrae la marca del producto"""
        if brand_hint:
            return self.normalize_brand(brand_hint, name)
        
        # Detectar marca desde el nombre
        detected_brand = self.detect_brand_from_product_name(name)
        if detected_brand:
            return detected_brand
        
        return ""

    def clean_final_name(self, name, brand):
        """Limpia el nombre final removiendo duplicaciones y palabras innecesarias"""
        if not name:
            return ""
        
        # Limpiar palabras no deseadas
        cleaned = self.clean_unwanted_words(name)
        
        # Remover duplicaciones de marca
        if brand:
            cleaned = self.remove_brand_duplication(cleaned, brand)
        
        # Limpiar separadores múltiples
        cleaned = self.clean_multiple_separators(cleaned)
        
        # Eliminar palabras sueltas comunes que quedan
        words_to_clean = ['ALL', 'DE', 'LA', 'EL', 'UN', 'UNA']
        for word in words_to_clean:
            cleaned = re.sub(rf'\b{re.escape(word)}\b', '', cleaned, flags=re.IGNORECASE)
        
        # Limpiar espacios y separadores finales
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        cleaned = re.sub(r'^[\s\-]+|[\s\-]+$', '', cleaned)
        
        return cleaned.strip()

    def extract_storage_capacity(self, name):
        """Extrae la capacidad de almacenamiento del nombre"""
        capacity, cleaned_name = self.extract_capacity_from_name(name)
        if capacity:
            normalized_capacity = self.normalize_capacity(capacity)
            return normalized_capacity, cleaned_name
        return "", name

def main():
    normalizer = DataNormalizer()
    
    # Configuración de archivos
    stores = {
        'clevercel': 'price_comparison/results_scrap/clevercel.json',
        'itech': 'price_comparison/results_scrap/itech.json',
        'phoneelectric': 'price_comparison/results_scrap/phoneelectric.json',
        'tooho': 'price_comparison/results_scrap/tooho.json',
        'celudmovil': 'price_comparison/results_scrap/celudmovil.json'
    }
    
    total_products = 0
    
    print("🔄 Iniciando normalización de datos...\n")
    
    for store_name, input_file in stores.items():
        output_file = f'price_comparison/results_normalized/{store_name}_normalized.json'
        count = normalizer.normalize_store_data(input_file, output_file)
        total_products += count
    
    print(f"\n✅ Normalización completada!")
    print(f"📊 Total de productos normalizados: {total_products}")
    print("📁 Archivos normalizados guardados en: price_comparison/results_normalized/")

if __name__ == "__main__":
    main() 