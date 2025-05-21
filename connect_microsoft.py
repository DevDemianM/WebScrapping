import requests
import msal
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de SharePoint
SHAREPOINT_URL = os.getenv('SHAREPOINT_URL')
SITE_ID = os.getenv('SITE_ID')
CLIENTE_ID = os.getenv('CLIENTE_ID')
CLIENTE_SECRETO = os.getenv('CLIENTE_SECRETO')
TENANT_ID = os.getenv('TENANT_ID')
SITE_NAME = os.getenv('SITE_NAME')

def obtener_token():
    """Obtiene el token de acceso usando MSAL"""
    app = msal.ConfidentialClientApplication(
        client_id=CLIENTE_ID,
        client_credential=CLIENTE_SECRETO,
        authority=f"https://login.microsoftonline.com/{TENANT_ID}"
    )
    
    scopes = ['https://graph.microsoft.com/.default']
    result = app.acquire_token_for_client(scopes=scopes)
    
    if "access_token" in result:
        return result["access_token"]
    else:
        raise Exception("Error al obtener el token de acceso")

def crear_carpeta_sharepoint(headers, drive_id, ruta_carpeta):
    """Crea una carpeta en SharePoint si no existe"""
    try:
        # Verificar si la carpeta existe
        check_response = requests.get(
            f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{ruta_carpeta}",
            headers=headers
        )
        
        if check_response.status_code == 404:
            # Crear la carpeta
            create_response = requests.post(
                f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root/children",
                headers=headers,
                json={
                    "name": os.path.basename(ruta_carpeta),
                    "folder": {},
                    "@microsoft.graph.conflictBehavior": "replace"
                }
            )
            create_response.raise_for_status()
            print(f"Carpeta '{ruta_carpeta}' creada exitosamente")
    except requests.exceptions.RequestException as e:
        print(f"Error al crear/verificar carpeta: {str(e)}")
        raise

def subir_archivo(ruta_archivo_local, ruta_destino_sharepoint):
    """Sube un archivo a SharePoint"""
    try:
        # Obtener token de acceso
        access_token = obtener_token()
        print("Token obtenido exitosamente")
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        # Obtener el ID del sitio usando el nombre
        print(f"Intentando obtener el sitio: micelu.sharepoint.com:/sites/{SITE_NAME}")
        site_response = requests.get(
            f"https://graph.microsoft.com/v1.0/sites/micelu.sharepoint.com:/sites/{SITE_NAME}",
            headers=headers
        )
        print(f"Respuesta del sitio: {site_response.text}")
        site_response.raise_for_status()
        site_id = site_response.json()["id"]
        print(f"ID del sitio obtenido: {site_id}")

        # Obtener la drive de documentos
        print("Obteniendo drives del sitio...")
        drive_response = requests.get(
            f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives",
            headers=headers
        )
        print(f"Respuesta de drives: {drive_response.text}")
        drive_response.raise_for_status()
        drive_id = drive_response.json()["value"][0]["id"]
        print(f"ID de drive obtenido: {drive_id}")

        # Crear la estructura de carpetas si no existe
        ruta_carpetas = os.path.dirname(ruta_destino_sharepoint)
        if ruta_carpetas:
            crear_carpeta_sharepoint(headers, drive_id, ruta_carpetas)

        # Leer el archivo local
        with open(ruta_archivo_local, 'rb') as file:
            file_content = file.read()

        # Subir el archivo
        upload_response = requests.put(
            f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{ruta_destino_sharepoint}:/content",
            headers={"Authorization": f"Bearer {access_token}"},
            data=file_content
        )
        upload_response.raise_for_status()
        print(f"Archivo subido exitosamente a {ruta_destino_sharepoint}")

    except Exception as e:
        print(f"Error al subir el archivo: {str(e)}")
        raise

def subir_archivos_results_scrap():
    """Sube todos los archivos CSV de la carpeta results_scrap a SharePoint"""
    try:
        # Obtener la fecha actual
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        
        # Ruta de la carpeta results_scrap
        carpeta_results = os.path.join(os.path.dirname(os.path.abspath(__file__)), "price_comparison", "results_scrap")
        
        # Verificar si la carpeta existe
        if not os.path.exists(carpeta_results):
            raise FileNotFoundError(f"La carpeta {carpeta_results} no existe")
        
        # Obtener lista de archivos CSV
        archivos_csv = [f for f in os.listdir(carpeta_results) if f.endswith('.csv')]
        
        if not archivos_csv:
            print("No se encontraron archivos CSV en la carpeta results_scrap")
            return
        
        print(f"Encontrados {len(archivos_csv)} archivos CSV para subir")
        
        # Subir cada archivo
        for archivo in archivos_csv:
            # Crear nombre del archivo con fecha
            nombre_base = os.path.splitext(archivo)[0]
            nombre_archivo_sharepoint = f"{nombre_base}_{fecha_actual}.csv"
            
            # Rutas completas
            ruta_local = os.path.join(carpeta_results, archivo)
            ruta_sharepoint = f"results_scrap/{nombre_archivo_sharepoint}"
            
            print(f"\nSubiendo archivo: {archivo}")
            subir_archivo(ruta_local, ruta_sharepoint)
            
        print("\n✅ Todos los archivos han sido subidos exitosamente")
        
    except Exception as e:
        print(f"Error al procesar los archivos: {str(e)}")
        raise

# Ejecutar el script
if __name__ == "__main__":
    subir_archivos_results_scrap() 