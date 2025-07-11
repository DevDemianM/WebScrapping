# 📖 MANUAL DEL PROYECTO - WEB SCRAPING MICELU

## 📋 TABLA DE CONTENIDOS
1. [Descripción General](#descripción-general)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Instalación y Configuración](#instalación-y-configuración)
4. [Uso del Sistema](#uso-del-sistema)
5. [Spiders Configurados](#spiders-configurados)
6. [Normalización de Datos](#normalización-de-datos)
7. [Integración con SharePoint](#integración-con-sharepoint)
8. [Automatización](#automatización)
9. [Mantenimiento](#mantenimiento)
10. [Solución de Problemas](#solución-de-problemas)

---

## 🎯 DESCRIPCIÓN GENERAL

**Proyecto**: Sistema de Web Scraping para Comparación de Precios de Dispositivos Móviles
**Cliente**: MICELU
**Objetivo**: Automatizar la recolección, normalización y análisis de precios de dispositivos móviles de múltiples tiendas online colombianas.

### ✨ Características Principales
- ✅ **Web Scraping** de 5 tiendas online
- ✅ **Normalización inteligente** de datos
- ✅ **Filtrado automático** (solo productos NUEVOS y SEMINUEVOS)
- ✅ **Detección automática** de marcas y especificaciones
- ✅ **Subida automática** a SharePoint
- ✅ **Ejecución programada** semanal
- ✅ **Informes detallados** de estadísticas

---

## 🏗️ ARQUITECTURA DEL SISTEMA

```
WebScrappingMicelu/
├── 📁 price_comparison/           # Proyecto Scrapy principal
│   ├── 📁 spiders/               # Spiders para cada tienda
│   │   ├── celudmovil.py         # 🕷️ Spider para Celudmovil
│   │   ├── clevercel.py          # 🕷️ Spider para Clevercel
│   │   ├── phoneelectric.py      # 🕷️ Spider para Phoneelectric
│   │   ├── itech.py              # 🕷️ Spider para Itech
│   │   └── tooho.py              # 🕷️ Spider para Tooho
│   ├── 📁 results_scrap/         # Datos sin procesar (JSON)
│   ├── 📁 results_normalized/    # Datos normalizados (JSON)
│   ├── items.py                  # Estructura de datos
│   ├── settings.py               # Configuración de Scrapy
│   └── scrapy.cfg                # Configuración del proyecto
├── normalize_data.py             # 🧠 Motor de normalización
├── connect_microsoft.py          # ☁️ Integración con SharePoint
├── run_complete_process.py       # 🚀 Ejecutor del proceso completo
├── schedule_task.py              # ⏰ Configurador de tareas
├── requirements.txt              # 📦 Dependencias
└── .env                          # 🔐 Variables de entorno
```

---

## ⚙️ INSTALACIÓN Y CONFIGURACIÓN

### 📋 Requisitos Previos
- **Python 3.8+**
- **Windows 10/11** (para tareas programadas)
- **Conexión a Internet** estable
- **Acceso a SharePoint** (opcional)

### 🔧 Instalación

1. **Clonar o descargar el proyecto**
```bash
git clone [URL_DEL_REPOSITORIO]
cd WebScrappingMicelu
```

2. **Crear entorno virtual**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno** (crear archivo `.env`)
```env
# SharePoint Configuration
SHAREPOINT_URL=https://micelu.sharepoint.com
SITE_NAME=ProyectosMICELU
CLIENTE_ID=tu_client_id
CLIENTE_SECRETO=tu_client_secret
TENANT_ID=tu_tenant_id
```

---

## 🚀 USO DEL SISTEMA

### 🎯 Ejecución Completa (Recomendado)
```bash
python run_complete_process.py
```
**Esto ejecuta**: Scraping → Normalización → Subida a SharePoint

### 🔍 Ejecuciones Específicas

**Solo Scraping**:
```bash
cd price_comparison
scrapy crawl [nombre_spider]  # celudmovil, tooho, clevercel, itech, phoneelectric
```

**Solo Normalización**:
```bash
python normalize_data.py
```

**Configurar Tarea Programada**:
```bash
python schedule_task.py
```

**Probar Tarea Programada**:
```bash
python schedule_task.py --test
```

---

## 🕷️ SPIDERS CONFIGURADOS

### 1. **🏪 Celudmovil** (`celudmovil.py`)
- **URL**: https://www.celudmovil.com.co
- **Productos**: Celulares, tablets, accesorios
- **Características**: Múltiples categorías, paginación automática

### 2. **🏪 Clevercel** (`clevercel.py`)
- **URL**: https://www.clevercel.co
- **Productos**: Samsung, iPhone, Apple Watch, otras marcas
- **Características**: Variantes complejas, detección de condiciones, JSON-LD

### 3. **🏪 Phoneelectric** (`phoneelectric.py`)
- **URL**: https://www.phonelectrics.com
- **Productos**: Xiaomi, Samsung, Apple, accesorios
- **Características**: Múltiples subcategorías por marca

### 4. **🏪 Itech** (`itech.py`)
- **URL**: https://itechcolombia.co
- **Productos**: Apple, Samsung, PlayStation, Xiaomi
- **Características**: Control de duplicados, paginación inteligente

### 5. **🏪 Tooho** (`tooho.py`)
- **URL**: https://www.tohoo.store
- **Productos**: Celulares, relojes, audio, computadores
- **Características**: Plataforma VTEX, precios dinámicos

---

## 🧠 NORMALIZACIÓN DE DATOS

### 🎯 Objetivos de la Normalización
- **Unificar formatos** de nombres de productos
- **Detectar marcas** automáticamente
- **Extraer especificaciones** (almacenamiento, RAM, etc.)
- **Filtrar productos** (solo NUEVOS y SEMINUEVOS)
- **Eliminar duplicaciones** y palabras irrelevantes

### 📝 Proceso de Normalización

#### 1. **Limpieza Inicial**
- Eliminación de tildes y caracteres especiales
- Conversión a mayúsculas
- Limpieza de patrones EXH → USADO

#### 2. **Detección de Marcas**
```python
# Marcas soportadas con prioridad
APPLE → iPhone, iPad, MacBook, AirPods
SAMSUNG → Galaxy
XIAOMI → Redmi, Poco, Mi
HUAWEI → Honor
MOTOROLA → Moto
OPPO → Realme, OnePlus
VIVO → iQOO
```

#### 3. **Filtros Aplicados**
- ✅ **Solo NUEVOS y SEMINUEVOS**
- ❌ Descartar: USADO, COMO NUEVO, OPEN BOX, CPO
- ❌ Eliminar: Productos de LAMPERT
- ❌ Quitar: Colores, materiales, palabras técnicas irrelevantes

#### 4. **Detección de Especificaciones**
- **Almacenamiento**: 128GB, 256GB, 512GB, 1TB
- **RAM**: Se elimina para evitar confusión con almacenamiento
- **Red**: Se mantiene 4G/5G para dispositivos móviles
- **SIM**: Detección automática (SIM FÍSICA/VIRTUAL)

#### 5. **Formato Final**
```
MARCA MODELO ESPECIFICACIONES SIM_TYPE CONDICION ALMACENAMIENTO
Ejemplo: "APPLE IPHONE 16 PRO 5G SIM FISICA NUEVO 256GB"
```

---

## ☁️ INTEGRACIÓN CON SHAREPOINT

### 🔐 Configuración de Autenticación
1. **Registrar aplicación** en Azure AD
2. **Obtener credenciales**:
   - Client ID
   - Client Secret  
   - Tenant ID
3. **Configurar permisos** de SharePoint

### 📤 Proceso de Subida
- **Carpeta destino**: `results_normalized/`
- **Formato**: `{tienda}_normalized_{fecha}.json`
- **Frecuencia**: Cada ejecución completa
- **Verificación**: Logs detallados de cada subida

### 📊 Estructura en SharePoint
```
ProyectosMICELU/
└── 📁 results_normalized/
    ├── celudmovil_normalized_2025-06-20.json
    ├── clevercel_normalized_2025-06-20.json
    ├── phoneelectric_normalized_2025-06-20.json
    ├── itech_normalized_2025-06-20.json
    └── tooho_normalized_2025-06-20.json
```

---

## ⏰ AUTOMATIZACIÓN

### 🗓️ Tarea Programada
- **Nombre**: `WebScrappingMicelu_CompleteProcess`
- **Frecuencia**: Semanal
- **Día**: Martes
- **Hora**: 9:00 AM
- **Proceso**: Completo (Scraping + Normalización + SharePoint)

### 🔄 Configuración Automática
```bash
python schedule_task.py  # Configura la tarea
```

### 📊 Monitoreo
- Logs detallados en cada ejecución
- Estadísticas por tienda
- Reportes de errores automáticos
- Verificación de archivos subidos

---

## 🔧 MANTENIMIENTO

### 📅 Tareas Regulares

#### **Semanales**
- [ ] Verificar ejecución automática
- [ ] Revisar logs de errores
- [ ] Validar archivos en SharePoint

#### **Mensuales**
- [ ] Actualizar selectores si cambian las páginas
- [ ] Revisar nuevos productos no capturados
- [ ] Optimizar filtros de normalización
- [ ] Backup de configuraciones

#### **Trimestrales**
- [ ] Actualizar dependencias (`pip install -U -r requirements.txt`)
- [ ] Revisar credenciales de SharePoint
- [ ] Análisis de rendimiento
- [ ] Documentación de cambios

### 🛠️ Archivos Críticos para Backup
- `.env` (credenciales)
- `normalize_data.py` (lógica de normalización)
- `price_comparison/spiders/*.py` (spiders)
- `requirements.txt` (dependencias)

---

## 🆘 SOLUCIÓN DE PROBLEMAS

### 🚨 Problemas Comunes

#### **Error: Spider no encuentra productos**
```bash
# Verificar selectores CSS
cd price_comparison
scrapy shell "https://URL_DE_LA_TIENDA"
# Probar selectores en la consola
```

#### **Error: "Module not found"**
```bash
# Instalar dependencias faltantes
pip install -r requirements.txt
```

#### **Error: SharePoint no responde**
```bash
# Verificar credenciales en .env
# Verificar conexión a internet
# Regenerar tokens de Azure AD
```

#### **Error: Tarea programada no se ejecuta**
```bash
# Verificar que existe la tarea
schtasks /query /tn "WebScrappingMicelu_CompleteProcess"

# Ejecutar manualmente para probar
python run_complete_process.py
```

### 🔍 Debugging

#### **Logs Detallados**
```bash
# Ejecutar spider con logs
cd price_comparison
scrapy crawl celudmovil -L DEBUG
```

#### **Verificar Normalización**
```python
# Probar normalización individual
from normalize_data import DataNormalizer
normalizer = DataNormalizer()
resultado = normalizer.normalize_product(
    "SAMSUNG GALAXY S24 ULTRA 256GB NUEVO",
    "Samsung", "3000000", "test", "url"
)
print(resultado)
```

---

## 📈 ESTADÍSTICAS TÍPICAS

### 📊 Rendimiento Esperado
- **Tiempo de ejecución**: 6-8 minutos
- **Productos totales**: ~1,500-2,000
- **Productos filtrados**: ~1,600 (solo NUEVOS/SEMINUEVOS)
- **Tasa de éxito**: >95%

### 🏪 Distribución por Tienda
1. **Celudmovil**: ~38% (600+ productos)
2. **Clevercel**: ~35% (570+ productos)  
3. **Phoneelectric**: ~16% (250+ productos)
4. **Tooho**: ~6% (90+ productos)
5. **Itech**: ~5% (75+ productos)

---

## ✅ CHECKLIST DE VERIFICACIÓN

### 🎯 Antes de Ejecutar
- [ ] Entorno virtual activado
- [ ] Variables de entorno configuradas
- [ ] Conexión a internet estable
- [ ] Espacio suficiente en disco

### 🎯 Después de Ejecutar
- [ ] Verificar logs sin errores críticos
- [ ] Comprobar archivos generados
- [ ] Validar productos normalizados
- [ ] Confirmar subida a SharePoint

### 🎯 Mantenimiento Regular
- [ ] Actualizar dependencias
- [ ] Revisar selectores
- [ ] Backup de configuración
- [ ] Documentar cambios

---

## 📝 HISTORIAL DE VERSIONES

### v1.0 - Versión Inicial
- ✅ 5 spiders configurados
- ✅ Normalización avanzada
- ✅ Integración SharePoint
- ✅ Automatización semanal

---

*Última actualización: Junio 2025*
*Desarrollado para MICELU* 