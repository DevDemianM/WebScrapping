#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
EJECUTOR DEL PROCESO COMPLETO DE WEB SCRAPING
============================================

Este script ejecuta el proceso completo de:
1. Web scraping de todas las tiendas
2. Normalización de datos
3. Subida a SharePoint

Ejecutar con: python ejecutar_proceso_completo.py
"""

import os
import subprocess
import json
from datetime import datetime
from normalize_data import DataNormalizer

# Intentar importar connect_microsoft, pero continuar si no está disponible
try:
    from connect_microsoft import subir_archivos_normalizados
    SHAREPOINT_DISPONIBLE = True
except ImportError:
    print("ADVERTENCIA: Modulo de SharePoint no disponible. Se omitira la subida.")
    SHAREPOINT_DISPONIBLE = False

def ejecutar_spider(spider_name):
    """Ejecuta un spider específico y guarda los resultados en JSON"""
    try:
        # Ruta del archivo de salida
        output_path = f"price_comparison/results_scrap/{spider_name}.json"
        # Borrar el archivo si existe antes de ejecutar el spider
        if os.path.exists(output_path):
            os.remove(output_path)
        # Crear el comando para ejecutar el spider
        comando = f"scrapy crawl {spider_name} -o results_scrap/{spider_name}.json"
        # Ejecutar el comando
        print(f"🕷️ Ejecutando spider: {spider_name}")
        resultado = subprocess.run(comando, shell=True, capture_output=True, text=True, cwd="price_comparison")
        if resultado.returncode == 0:
            print(f"[OK] Spider {spider_name} ejecutado exitosamente")
            return True
        else:
            print(f"[ERROR] Error al ejecutar spider {spider_name}:")
            print(resultado.stderr)
            return False
    except Exception as e:
        print(f"[ERROR] Error inesperado al ejecutar spider {spider_name}: {str(e)}")
        return False

def normalizar_datos():
    """Normaliza todos los datos después del scraping"""
    try:
        print("\n[INFO] Iniciando normalizacion de datos...")
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
        
        for store_name, input_file in stores.items():
            if os.path.exists(input_file):
                output_file = f'price_comparison/results_normalized/{store_name}_normalized.json'
                count = normalizer.normalize_store_data(input_file, output_file)
                total_products += count
            else:
                print(f"[ADVERTENCIA] Archivo no encontrado: {input_file}")
        
        print(f"[OK] Normalizacion completada! Total: {total_products} productos")
        return True, total_products
    except Exception as e:
        print(f"[ERROR] Error durante la normalizacion: {str(e)}")
        return False, 0

def mostrar_estadisticas():
    """Muestra estadísticas detalladas de los archivos normalizados"""
    try:
        carpeta_normalized = "price_comparison/results_normalized"
        
        if not os.path.exists(carpeta_normalized):
            print("[ADVERTENCIA] No se encontro carpeta de archivos normalizados")
            return
        
        archivos_normalizados = [f for f in os.listdir(carpeta_normalized) if f.endswith('_normalized.json')]
        
        print(f"\n[ESTADISTICAS DETALLADAS]")
        print("=" * 70)
        
        total_productos = 0
        estadisticas_por_tienda = {}
        
        for archivo in archivos_normalizados:
            tienda = archivo.replace('_normalized.json', '').upper()
            ruta_archivo = os.path.join(carpeta_normalized, archivo)
            
            try:
                with open(ruta_archivo, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    cantidad = len(data)
                    total_productos += cantidad
                    estadisticas_por_tienda[tienda] = cantidad
                    
                    print(f"📦 {tienda:<15}: {cantidad:>6} productos")
                    
                    # Mostrar ejemplo del primer producto
                    if data:
                        ejemplo = data[0]
                        print(f"   Ejemplo: {ejemplo['name'][:65]}")
                        print(f"   Precio:  {ejemplo['price']}")
                        print()
            except Exception as e:
                print(f"[ERROR] {tienda}: Error leyendo archivo - {str(e)}")
        
        print("=" * 70)
        print(f"🎯 TOTAL GENERAL: {total_productos:>6} productos normalizados")
        print("=" * 70)
        
        # Mostrar distribución porcentual
        print(f"\n📈 DISTRIBUCIÓN POR TIENDA:")
        print("-" * 40)
        for tienda, cantidad in sorted(estadisticas_por_tienda.items(), key=lambda x: x[1], reverse=True):
            porcentaje = (cantidad / total_productos * 100) if total_productos > 0 else 0
            print(f"{tienda:<15}: {porcentaje:>5.1f}% ({cantidad} productos)")
        print("-" * 40)
        
        return total_productos
        
    except Exception as e:
        print(f"[ERROR] Error mostrando estadisticas: {str(e)}")
        return 0

def verificar_archivos_entrada():
    """Verifica que existan los archivos de entrada necesarios"""
    carpeta_scrap = "price_comparison/results_scrap"
    if not os.path.exists(carpeta_scrap):
        print(f"[ERROR] Carpeta no encontrada: {carpeta_scrap}")
        return False
    
    archivos_requeridos = ['clevercel.json', 'itech.json', 'phoneelectric.json', 'tooho.json', 'celudmovil.json']
    archivos_encontrados = []
    
    for archivo in archivos_requeridos:
        ruta_archivo = os.path.join(carpeta_scrap, archivo)
        if os.path.exists(ruta_archivo):
            archivos_encontrados.append(archivo)
        else:
            print(f"[ADVERTENCIA] Archivo no encontrado: {archivo}")
    
    print(f"[INFO] Archivos encontrados: {len(archivos_encontrados)}/{len(archivos_requeridos)}")
    return len(archivos_encontrados) > 0

def main():
    """Función principal que ejecuta todo el proceso"""
    print("INICIANDO PROCESO COMPLETO DE WEB SCRAPING")
    print("=" * 70)
    print(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Lista de spiders a ejecutar
    spiders = [
        "celudmovil",
        "tooho", 
        "clevercel",
        "itech",
        "phoneelectric"
    ]
    
    # PASO 1: Ejecutar spiders
    print("\n[PASO 1: EJECUTANDO WEB SCRAPING]")
    print("-" * 40)
    
    spiders_exitosos = 0
    for i, spider in enumerate(spiders, 1):
        print(f"\n[{i}/{len(spiders)}] {spider.upper()}")
        if ejecutar_spider(spider):
            spiders_exitosos += 1
    
    print(f"\n[OK] Scraping completado: {spiders_exitosos}/{len(spiders)} spiders exitosos")
    
    if spiders_exitosos == 0:
        print("[ERROR] No se pudo ejecutar ningun spider. Abortando proceso.")
        return
    
    # Verificar archivos generados
    if not verificar_archivos_entrada():
        print("[ERROR] No se encontraron archivos de datos. Abortando normalizacion.")
        return
    
    # PASO 2: Normalizar datos
    print("\n[PASO 2: NORMALIZANDO DATOS]")
    print("-" * 40)
    
    exito_normalizacion, total_productos = normalizar_datos()
    
    if not exito_normalizacion:
        print("[ERROR] Error en la normalizacion. Abortando proceso.")
        return
    
    # Mostrar estadísticas detalladas
    total_productos = mostrar_estadisticas()
    
    # PASO 3: Subir a SharePoint (opcional)
    if SHAREPOINT_DISPONIBLE:
        print("\n[PASO 3: SUBIENDO A SHAREPOINT]")
        print("-" * 40)
        
        try:
            if subir_archivos_normalizados():
                print("[OK] Archivos subidos exitosamente a SharePoint")
            else:
                print("[ADVERTENCIA] Algunos archivos no se pudieron subir a SharePoint")
        except Exception as e:
            print(f"[ERROR] Error al subir a SharePoint: {str(e)}")
            print("[INFO] Los archivos estan disponibles localmente en results_normalized/")
    else:
        print("\n[PASO 3: ARCHIVOS LISTOS LOCALMENTE]")
        print("-" * 40)
        print("[INFO] Los archivos normalizados estan disponibles en:")
        print("   price_comparison/results_normalized/")
        print("[INFO] Para subir a SharePoint, configurar connect_microsoft.py")
    
    # Resumen final
    print("\n" + "=" * 70)
    print("[PROCESO COMPLETADO EXITOSAMENTE]")
    print("=" * 70)
    print(f"Productos procesados: {total_productos}")
    print(f"Finalizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Archivos disponibles en: price_comparison/results_normalized/")
    print("=" * 70)

if __name__ == "__main__":
    main() 