# 🕷️ Web Scraping MICELU - Comparación de Precios

Sistema automatizado de web scraping para comparación de precios de dispositivos móviles de múltiples tiendas online colombianas.

## 🚀 Inicio Rápido

### 1. Instalación
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configuración
Crear archivo `.env` con credenciales de SharePoint:
```env
SHAREPOINT_URL=https://micelu.sharepoint.com
SITE_NAME=ProyectosMICELU
CLIENTE_ID=tu_client_id
CLIENTE_SECRETO=tu_client_secret
TENANT_ID=tu_tenant_id
```

### 3. Ejecución Completa
```bash
python run_complete_process.py
```

## 🏪 Tiendas Monitoreadas

- **Celudmovil** - https://www.celudmovil.com.co
- **Clevercel** - https://www.clevercel.co  
- **Phoneelectric** - https://www.phonelectrics.com
- **Itech** - https://itechcolombia.co
- **Tooho** - https://www.tohoo.store

## 📊 Características

✅ **Scraping de 5 tiendas** simultáneamente  
✅ **Normalización inteligente** de productos  
✅ **Filtrado automático** (solo NUEVOS y SEMINUEVOS)  
✅ **Detección de marcas** y especificaciones  
✅ **Subida automática** a SharePoint  
✅ **Ejecución programada** semanal (Martes 9:00 AM)  

## 🎯 Resultados Típicos

- **~1,600 productos** normalizados
- **5-8 minutos** de ejecución
- **Filtros aplicados**: Solo productos nuevos/seminuevos
- **Formato unificado**: Marca, modelo, especificaciones, condición

## ⏰ Automatización

Para configurar la ejecución automática semanal:
```bash
python schedule_task.py
```

## 📖 Documentación Completa

Ver [MANUAL_PROYECTO_WEBSCRAPING_MICELU.md](MANUAL_PROYECTO_WEBSCRAPING_MICELU.md) para documentación detallada.

## 📁 Estructura del Proyecto

```
WebScrappingMicelu/
├── 📁 price_comparison/        # Spiders de Scrapy
├── normalize_data.py          # Motor de normalización  
├── connect_microsoft.py       # Integración SharePoint
├── run_complete_process.py    # Proceso completo
└── schedule_task.py           # Automatización
```

## 🛠️ Comandos Útiles

| Comando | Descripción |
|---------|-------------|
| `python run_complete_process.py` | Proceso completo |
| `python normalize_data.py` | Solo normalización |
| `python schedule_task.py` | Configurar automatización |
| `python schedule_task.py --test` | Probar ejecución |

---

#El archivo Automatización es el Workflow de N8N
