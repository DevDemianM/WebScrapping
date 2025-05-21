import os
import subprocess
from datetime import datetime
from connect_microsoft import subir_archivo

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

def subir_archivos_json():
    """Sube todos los archivos JSON a SharePoint"""
    try:
        # Obtener la fecha actual
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        
        # Ruta de la carpeta results_scrap
        carpeta_results = os.path.join(os.path.dirname(os.path.abspath(__file__)), "price_comparison", "results_scrap")
        
        # Verificar si la carpeta existe
        if not os.path.exists(carpeta_results):
            raise FileNotFoundError(f"La carpeta {carpeta_results} no existe")
        
        # Obtener lista de archivos JSON
        archivos_json = [f for f in os.listdir(carpeta_results) if f.endswith('.json')]
        
        if not archivos_json:
            print("[INFO] No se encontraron archivos JSON en la carpeta results_scrap")
            return
        
        print(f"\n[INFO] Encontrados {len(archivos_json)} archivos JSON para subir")
        
        # Mapeo de nombres de archivos a inglés
        nombre_mapping = {
            "celudmovil": "celudmovil",
            "tooho": "tooho",
            "clevercel": "clevercel",
            "itech": "itech",
            "phoneelectric": "phoneelectric"
        }
        
        # Subir cada archivo
        for archivo in archivos_json:
            # Obtener el nombre base sin extensión
            nombre_base = os.path.splitext(archivo)[0]
            
            # Usar el nombre en inglés del mapping o mantener el original si no está en el mapping
            nombre_ingles = nombre_mapping.get(nombre_base, nombre_base)
            
            # Crear nombre del archivo con fecha
            nombre_archivo_sharepoint = f"{nombre_ingles}_{fecha_actual}.json"
            
            # Rutas completas
            ruta_local = os.path.join(carpeta_results, archivo)
            ruta_sharepoint = f"results_scrap/{nombre_archivo_sharepoint}"
            
            print(f"\n[INFO] Subiendo archivo: {archivo}")
            subir_archivo(ruta_local, ruta_sharepoint)
            
        print("\n[OK] Todos los archivos han sido subidos exitosamente")
        
    except Exception as e:
        print(f"[ERROR] Error al procesar los archivos: {str(e)}")
        raise

def main():
    """Función principal que ejecuta todos los spiders y sube los resultados"""
    # Lista de spiders a ejecutar
    spiders = [
        "celudmovil",
        "tooho",
        "clevercel",
        "itech",
        "phoneelectric"
    ]
    
    # Asegurarse de estar en el directorio correcto
    os.chdir("price_comparison")
    
    # Ejecutar cada spider
    for spider in spiders:
        ejecutar_spider(spider)
    
    # Subir los archivos JSON generados
    subir_archivos_json()

if __name__ == "__main__":
    main() 