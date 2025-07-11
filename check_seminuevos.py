#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VERIFICADOR DE PRODUCTOS SEMINUEVOS
===================================

Este script analiza los archivos originales y normalizados para detectar
productos seminuevos y verificar si se están procesando correctamente.
"""

import json
import os
import re
from colorama import init, Fore, Style

# Inicializar colorama para colores en terminal
init()

def load_json_file(file_path):
    """Carga un archivo JSON y maneja posibles errores"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"{Fore.RED}Error cargando {file_path}: {str(e)}{Style.RESET_ALL}")
        return []

def detect_seminuevo_patterns(text):
    """Detecta patrones de productos seminuevos en un texto"""
    if not text:
        return False
    
    text = text.upper()
    patterns = [
        r'\bEXH\b', r'\bEXH\s*PREMIUM\b',
        r'\bDE\s+EXH\b', r'\bDE\s+EXH\s*PREMIUM\b',
        r'\bSEMINUEVO\b', r'\bSEMI\s*NUEVO\b'
    ]
    
    for pattern in patterns:
        if re.search(pattern, text):
            return True
    
    return False

def analyze_store(store_name):
    """Analiza los archivos originales y normalizados de una tienda"""
    original_file = f"price_comparison/results_scrap/{store_name}.json"
    normalized_file = f"price_comparison/results_normalized/{store_name}_normalized.json"
    
    # Cargar datos
    original_data = load_json_file(original_file)
    normalized_data = load_json_file(normalized_file)
    
    # Contar productos originales con patrones de seminuevo
    seminuevo_patterns_count = 0
    potential_seminuevos = []
    
    for item in original_data:
        name = item.get('name', '')
        if detect_seminuevo_patterns(name):
            seminuevo_patterns_count += 1
            potential_seminuevos.append(name)
    
    # Contar productos normalizados con condición SEMINUEVO
    seminuevo_normalized_count = sum(1 for item in normalized_data if item.get('condition') == 'SEMINUEVO')
    
    # Mostrar resultados
    print(f"\n{Fore.CYAN}=== {store_name.upper()} ==={Style.RESET_ALL}")
    print(f"Total productos originales: {len(original_data)}")
    print(f"Total productos normalizados: {len(normalized_data)}")
    print(f"Productos con patrones de seminuevo: {seminuevo_patterns_count}")
    print(f"Productos normalizados como SEMINUEVO: {seminuevo_normalized_count}")
    
    # Calcular diferencia
    diff = seminuevo_patterns_count - seminuevo_normalized_count
    if diff > 0:
        print(f"{Fore.RED}⚠️ Se perdieron {diff} productos seminuevos durante la normalización{Style.RESET_ALL}")
        print("\nEjemplos de productos con patrones de seminuevo que podrían haberse perdido:")
        for i, name in enumerate(potential_seminuevos[:5]):
            print(f"{i+1}. {name}")
    elif diff < 0:
        print(f"{Fore.GREEN}✅ Se detectaron {abs(diff)} productos seminuevos adicionales durante la normalización{Style.RESET_ALL}")
    else:
        print(f"{Fore.GREEN}✅ Todos los productos seminuevos fueron correctamente procesados{Style.RESET_ALL}")
    
    return {
        "store": store_name,
        "original_count": len(original_data),
        "normalized_count": len(normalized_data),
        "seminuevo_patterns": seminuevo_patterns_count,
        "seminuevo_normalized": seminuevo_normalized_count,
        "diff": diff
    }

def main():
    """Función principal"""
    print(f"{Fore.YELLOW}🔍 VERIFICADOR DE PRODUCTOS SEMINUEVOS{Style.RESET_ALL}")
    print("=" * 60)
    
    stores = ['clevercel', 'itech', 'phoneelectric', 'tooho', 'celudmovil']
    results = []
    
    for store in stores:
        result = analyze_store(store)
        results.append(result)
    
    # Mostrar resumen
    print("\n" + "=" * 60)
    print(f"{Fore.YELLOW}📊 RESUMEN GENERAL{Style.RESET_ALL}")
    print("=" * 60)
    
    total_original = sum(r["original_count"] for r in results)
    total_normalized = sum(r["normalized_count"] for r in results)
    total_seminuevo_patterns = sum(r["seminuevo_patterns"] for r in results)
    total_seminuevo_normalized = sum(r["seminuevo_normalized"] for r in results)
    
    print(f"Total productos originales: {total_original}")
    print(f"Total productos normalizados: {total_normalized}")
    print(f"Total productos con patrones de seminuevo: {total_seminuevo_patterns}")
    print(f"Total productos normalizados como SEMINUEVO: {total_seminuevo_normalized}")
    
    total_diff = total_seminuevo_patterns - total_seminuevo_normalized
    if total_diff > 0:
        print(f"{Fore.RED}⚠️ TOTAL: Se perdieron {total_diff} productos seminuevos durante la normalización{Style.RESET_ALL}")
    elif total_diff < 0:
        print(f"{Fore.GREEN}✅ TOTAL: Se detectaron {abs(total_diff)} productos seminuevos adicionales durante la normalización{Style.RESET_ALL}")
    else:
        print(f"{Fore.GREEN}✅ TOTAL: Todos los productos seminuevos fueron correctamente procesados{Style.RESET_ALL}")
    
    print("=" * 60)

if __name__ == "__main__":
    main() 