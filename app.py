#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
APP - Panel de Control Web Scraping MICELU
==========================================

Aplicación Flask para controlar la ejecución del proceso completo:
1. Scraping de todas las tiendas
2. Normalización de datos
3. Subida a SharePoint
4. Trigger de n8n para generar Excel
"""

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import subprocess
import threading
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
CORS(app)

# Estado global del proceso
proceso_estado = {
    "ejecutando": False,
    "paso_actual": "",
    "progreso": 0,
    "mensaje": "",
    "inicio": None,
    "fin": None,
    "error": None
}

# URL del webhook de n8n (configurar según tu instalación)
N8N_WEBHOOK_URL = os.getenv('N8N_WEBHOOK_URL', 'http://localhost:5678/webhook/actualizar-excel')

def ejecutar_proceso_completo():
    """Ejecuta el proceso completo en un hilo separado"""
    global proceso_estado
    
    try:
        proceso_estado["ejecutando"] = True
        proceso_estado["inicio"] = datetime.now().isoformat()
        proceso_estado["error"] = None
        proceso_estado["paso_actual"] = "Iniciando proceso"
        proceso_estado["progreso"] = 5
        proceso_estado["mensaje"] = "Iniciando proceso de web scraping..."
        
        print("[APP] Iniciando proceso completo...")
        
        # Configurar entorno para UTF-8
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        # Ejecutar proceso sin capturar salida para que se vea en consola
        proceso = subprocess.Popen(
            ["python", "-u", "run_complete_process.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=0,
            universal_newlines=True,
            encoding='utf-8',
            errors='replace',  # Reemplazar caracteres problemáticos
            env=env
        )
        
        # Leer salida línea por línea
        while True:
            linea = proceso.stdout.readline()
            
            if not linea:
                if proceso.poll() is not None:
                    break
                continue
            
            linea = linea.strip()
            
            # Mostrar en consola de VS Code
            print(f"[PROCESO] {linea}")
            
            # Detectar progreso según patrones en la salida
            if "[1/5]" in linea or "celudmovil" in linea.lower():
                proceso_estado["paso_actual"] = "Scraping: Celudmovil"
                proceso_estado["progreso"] = 15
                proceso_estado["mensaje"] = "Extrayendo productos de Celudmovil..."
            
            elif "[2/5]" in linea or ("tooho" in linea.lower() and "spider" in linea.lower()):
                proceso_estado["paso_actual"] = "Scraping: Tooho"
                proceso_estado["progreso"] = 25
                proceso_estado["mensaje"] = "Extrayendo productos de Tooho..."
            
            elif "[3/5]" in linea or ("clevercel" in linea.lower() and "spider" in linea.lower()):
                proceso_estado["paso_actual"] = "Scraping: Clevercel"
                proceso_estado["progreso"] = 35
                proceso_estado["mensaje"] = "Extrayendo productos de Clevercel..."
            
            elif "[4/5]" in linea or ("itech" in linea.lower() and "spider" in linea.lower()):
                proceso_estado["paso_actual"] = "Scraping: iTech"
                proceso_estado["progreso"] = 45
                proceso_estado["mensaje"] = "Extrayendo productos de iTech..."
            
            elif "[5/5]" in linea or ("phoneelectric" in linea.lower() and "spider" in linea.lower()):
                proceso_estado["paso_actual"] = "Scraping: PhoneElectric"
                proceso_estado["progreso"] = 55
                proceso_estado["mensaje"] = "Extrayendo productos de PhoneElectric..."
            
            elif "scraping completado" in linea.lower() or "5/5 spiders exitosos" in linea.lower():
                proceso_estado["paso_actual"] = "Scraping completado"
                proceso_estado["progreso"] = 65
                proceso_estado["mensaje"] = "Scraping completado exitosamente"
            
            elif "paso 2" in linea.lower() or "normalizando" in linea.lower():
                proceso_estado["paso_actual"] = "Normalizando datos"
                proceso_estado["progreso"] = 70
                proceso_estado["mensaje"] = "Normalizando y limpiando datos..."
            
            elif "normalizacion completada" in linea.lower():
                proceso_estado["paso_actual"] = "Normalización completada"
                proceso_estado["progreso"] = 75
                proceso_estado["mensaje"] = "Datos normalizados correctamente"
            
            elif "paso 3" in linea.lower() or "subiendo" in linea.lower():
                proceso_estado["paso_actual"] = "Subiendo a SharePoint"
                proceso_estado["progreso"] = 80
                proceso_estado["mensaje"] = "Subiendo archivos a SharePoint..."
            
            elif "proceso completado" in linea.lower() or "archivos subidos" in linea.lower():
                proceso_estado["paso_actual"] = "Proceso completado"
                proceso_estado["progreso"] = 90
                proceso_estado["mensaje"] = "Archivos actualizados en SharePoint. Ejecuta n8n manualmente para generar Excel."
        
        # Esperar a que el proceso termine completamente
        returncode = proceso.wait(timeout=600)
        
        print(f"[APP] Proceso terminado con código: {returncode}")
        
        # Verificar si hubo errores
        if returncode != 0:
            raise Exception(f"El proceso termino con codigo de error: {returncode}")
        
        proceso_estado["fin"] = datetime.now().isoformat()
        
        # Intentar trigger de n8n (opcional)
        try:
            print("[APP] Intentando llamar a n8n...")
            response = requests.post(
                N8N_WEBHOOK_URL,
                json={"trigger": "manual", "timestamp": datetime.now().isoformat()},
                timeout=10
            )
            
            if response.status_code == 200:
                proceso_estado["progreso"] = 100
                proceso_estado["mensaje"] = "Proceso completado exitosamente. Excel actualizado."
                print("[APP] n8n respondio correctamente")
        
        except requests.exceptions.RequestException as e:
            print(f"[APP] n8n no disponible: {e}")
            pass
        
    except subprocess.TimeoutExpired:
        print("[APP] ERROR: Timeout")
        proceso_estado["error"] = "El proceso excedio el tiempo limite de 10 minutos"
        proceso_estado["mensaje"] = "Error: Timeout"
        proceso_estado["progreso"] = 0
    
    except Exception as e:
        print(f"[APP] ERROR: {e}")
        proceso_estado["error"] = str(e)
        proceso_estado["mensaje"] = f"Error: {str(e)}"
        proceso_estado["progreso"] = 0
    
    finally:
        proceso_estado["ejecutando"] = False
        proceso_estado["paso_actual"] = "Completado" if not proceso_estado["error"] else "Error"
        print("[APP] Proceso finalizado")

@app.route('/api/status', methods=['GET'])
def get_status():
    """Obtiene el estado actual del proceso"""
    return jsonify(proceso_estado)

@app.route('/api/ejecutar', methods=['POST'])
def ejecutar():
    """Inicia la ejecución del proceso completo"""
    global proceso_estado
    
    if proceso_estado["ejecutando"]:
        return jsonify({
            "success": False,
            "message": "Ya hay un proceso en ejecución"
        }), 400
    
    # Reiniciar estado
    proceso_estado = {
        "ejecutando": True,
        "paso_actual": "Iniciando",
        "progreso": 0,
        "mensaje": "Preparando ejecución...",
        "inicio": None,
        "fin": None,
        "error": None
    }
    
    # Ejecutar en hilo separado
    thread = threading.Thread(target=ejecutar_proceso_completo)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        "success": True,
        "message": "Proceso iniciado correctamente"
    })

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/')
def index():
    """Página principal del panel de control"""
    return render_template('index.html')

if __name__ == '__main__':
    print("🚀 Servidor iniciado en http://localhost:5000")
    print("📊 Panel de control disponible en http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
