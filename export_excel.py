import os
import pandas as pd
from datetime import datetime

folder = "price_comparison/results_scrap"
# Obtener la fecha actual en formato YYYY-MM-DD
fecha_actual = datetime.now().strftime("%Y-%m-%d")
excel_output = f"price_comparison/competence/competence_data_{fecha_actual}.xlsx"

# Verificar si la carpeta de entrada existe
if not os.path.exists(folder):
    print(f"❌ Error: La carpeta '{folder}' no existe")
    exit(1)

# Verificar si la carpeta de salida existe, si no, crearla
if not os.path.exists("price_comparison/competence"):
    os.makedirs("price_comparison/competence")
    print("📁 Carpeta 'price_comparison/competence' creada")

# Obtener lista de archivos CSV
csv_files = [f for f in os.listdir(folder) if f.endswith('.csv')]

if not csv_files:
    print(f"❌ Error: No se encontraron archivos CSV en la carpeta '{folder}'")
    exit(1)

print(f"📁 Procesando {len(csv_files)} archivos CSV...")

with pd.ExcelWriter(excel_output, engine='openpyxl') as writer:
    for filename in csv_files:
        filepath = os.path.join(folder, filename)
        sheet_name = filename.replace(".csv", "")
        
        try:
            df = pd.read_csv(filepath)
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            print(f"✅ Añadida hoja: {sheet_name}")
        except Exception as e:
            print(f"❌ Error al procesar {filename}: {e}")

print(f"\n📁 Archivo Excel generado: {excel_output}")











