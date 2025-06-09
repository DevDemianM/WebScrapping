import os
import subprocess
from datetime import datetime
from connect_microsoft import subir_archivo
from normalize_data import DataNormalizer

def ejecutar_spider(spider_name):
    """Ejecuta un spider específico y guarda los resultados en JSON"""
    try:
        # Crear el comando para ejecutar el spider
        comando = f"scrapy crawl {spider_name} -o results_scrap/{spider_name}.json"
        
        # Ejecutar el comando
        print(f"\n[INFO] Ejecutando spider: {spider_name}")
        resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)
        
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
        print("\n[INFO] Iniciando normalización de datos...")
        normalizer = DataNormalizer()
        normalizer.normalize_all_stores()
        print("[OK] Normalización completada exitosamente")
        return True
    except Exception as e:
        print(f"[ERROR] Error durante la normalización: {str(e)}")
        return False

def subir_archivos_normalizados():
    """Sube todos los archivos normalizados a SharePoint"""
    try:
        # Obtener la fecha actual
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        
        # Ruta de la carpeta results_normalized
        carpeta_normalized = os.path.join(os.path.dirname(os.path.abspath(__file__)), "price_comparison", "results_normalized")
        
        # Verificar si la carpeta existe
        if not os.path.exists(carpeta_normalized):
            raise FileNotFoundError(f"La carpeta {carpeta_normalized} no existe")
        
        # Obtener lista de archivos normalizados
        archivos_normalizados = [f for f in os.listdir(carpeta_normalized) if f.endswith('_normalized.json')]
        
        if not archivos_normalizados:
            print("[INFO] No se encontraron archivos normalizados")
            return
        
        print(f"\n[INFO] Encontrados {len(archivos_normalizados)} archivos normalizados para subir")
        
        # Subir cada archivo normalizado
        for archivo in archivos_normalizados:
            # Extraer el nombre de la tienda (ej: clevercel_normalized.json -> clevercel)
            nombre_tienda = archivo.replace('_normalized.json', '')
            
            # Crear nombre del archivo con fecha
            nombre_archivo_sharepoint = f"{nombre_tienda}_normalized_{fecha_actual}.json"
            
            # Rutas completas
            ruta_local = os.path.join(carpeta_normalized, archivo)
            ruta_sharepoint = f"results_normalized/{nombre_archivo_sharepoint}"
            
            print(f"\n[INFO] Subiendo archivo normalizado: {archivo}")
            subir_archivo(ruta_local, ruta_sharepoint)
            
        print("\n[OK] Todos los archivos normalizados han sido subidos exitosamente")
        
    except Exception as e:
        print(f"[ERROR] Error al procesar los archivos normalizados: {str(e)}")
        raise

def main():
    """Función principal que ejecuta todos los spiders, normaliza y sube los resultados"""
    # Lista de spiders a ejecutar
    spiders = [
        "celudmovil",
        "tooho",
        "clevercel",
        "itech", 
        "phoneelectric"
    ]
    
    print("[INFO] 🚀 Iniciando proceso completo de scraping...")
    print("=" * 60)
    
    # Asegurarse de estar en el directorio correcto
    os.chdir("price_comparison")
    
    # Ejecutar cada spider
    print("\n[INFO] 📊 PASO 1: Ejecutando spiders...")
    for spider in spiders:
        ejecutar_spider(spider)
    
    # Volver al directorio raíz para la normalización
    os.chdir("..")
    
    # Normalizar los datos
    print("\n[INFO] 🔧 PASO 2: Normalizando datos...")
    if normalizar_datos():
        # Subir los archivos normalizados
        print("\n[INFO] ☁️ PASO 3: Subiendo archivos normalizados a SharePoint...")
        subir_archivos_normalizados()
        
        print("\n" + "=" * 60)
        print("✅ PROCESO COMPLETADO EXITOSAMENTE!")
        print("📁 Archivos normalizados subidos a SharePoint")
        print("=" * 60)
    else:
        print("\n❌ Error durante la normalización. No se subirán archivos.")
    
    # Mensaje final
    print(f"\n🕒 Proceso finalizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 