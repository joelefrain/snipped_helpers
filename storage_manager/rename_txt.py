import os
import re

# Ruta local donde se descargaron los archivos
local_base_path = 'path/to/your/local/base/path'
network_code = 'RA'

# Expresión regular para extraer la fecha de la línea 20
fecha_regex = re.compile(r"# HORA INICIO \(UTC-0\): (\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2})")

def get_date_from_txt(file_path):
    """Lee la línea 20 del archivo y extrae la fecha y hora."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lineas = f.readlines()
            if len(lineas) >= 20:
                match = fecha_regex.search(lineas[19])  # Línea 20 (índice 19)
                if match:
                    fecha = match.group(1).replace("-", "_")  # yyyy_mm_dd
                    hora = match.group(2).replace(":", "_")  # hh_mm_ss
                    return f"{fecha}_{hora}"
    except Exception as e:
        print(f"Error al leer {file_path}: {e}")
    return None

def rename_txt(local_base_path):
    """Recorre las subcarpetas y renombra los archivos agregando la fecha."""
    for root, _, files in os.walk(local_base_path):
        for file in files:
            if file.startswith(f"RED_{network_code}") and file.endswith(".txt"):
                file_path = os.path.join(root, file)
                nueva_fecha = get_date_from_txt(file_path)
                
                if nueva_fecha:
                    nuevo_nombre = f"{file[:-4]}_{nueva_fecha}.txt"  # Agregar fecha antes de .txt
                    nuevo_path = os.path.join(root, nuevo_nombre)
                    
                    try:
                        os.rename(file_path, nuevo_path)
                        print(f"Renombrado: {file} → {nuevo_nombre}")
                    except Exception as e:
                        print(f"Error al renombrar {file}: {e}")

# Ejecutar el renombrado
rename_txt(local_base_path)
