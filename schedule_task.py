import os
import subprocess
from datetime import datetime
import time

def create_scheduled_task(test_mode=False):
    """Creates a Windows scheduled task to run the spiders script"""
    try:
        # Get absolute paths
        script_path = os.path.abspath("run_complete_process.py")
        python_path = os.path.abspath("venv/Scripts/python.exe")
        
        if test_mode:
            print("[INFO] Ejecutando prueba inmediata...")
            print("[INFO] Esta prueba tiene un límite de tiempo de 5 minutos")
            
            # Ejecutar el script con timeout
            start_time = time.time()
            result = subprocess.run(
                f'"{python_path}" "{script_path}"',
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos de timeout
            )
            
            if result.returncode == 0:
                print("[OK] Prueba ejecutada exitosamente")
                print(f"[INFO] Tiempo de ejecución: {time.time() - start_time:.2f} segundos")
            else:
                print("[ERROR] Error en la prueba:")
                print(result.stderr)
            return
        
        # Create the scheduled task command
        command = f'schtasks /create /tn "WebScrappingMicelu_CompleteProcess" /tr "{python_path} {script_path}" /sc weekly /d TUE /st 09:00 /f'
        
        print("[INFO] Configurando tarea programada...")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[OK] Tarea programada creada exitosamente")
            print("\nDetalles de la tarea:")
            print("- Nombre: WebScrappingMicelu_CompleteProcess")
            print("- Frecuencia: Semanal")
            print("- Día: Martes")
            print("- Hora: 9:00 AM")
            print("- Proceso: Scraping + Normalización + Subida a SharePoint")
            print(f"- Script: {script_path}")
        else:
            print("[ERROR] Error al crear la tarea programada:")
            print(result.stderr)
            
    except subprocess.TimeoutExpired:
        print("[ERROR] La prueba excedió el tiempo límite de 5 minutos")
        print("[INFO] Esto puede indicar problemas con los spiders o la conexión")
    except Exception as e:
        print(f"[ERROR] Error inesperado: {str(e)}")

if __name__ == "__main__":
    import sys
    # Si se pasa el argumento --test, ejecutar en modo prueba
    test_mode = "--test" in sys.argv
    create_scheduled_task(test_mode) 