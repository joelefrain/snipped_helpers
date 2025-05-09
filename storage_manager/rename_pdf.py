import os
import re

# Ruta base donde están los archivos
local_base_path = 'path/to/your/local/base/path'
group_to_keep = '3'

# Patrón para extraer el último número antes del código
pattern = re.compile(r"^(?:[\d-]+-)?(\d+)-([a-zA-Z0-9]+)\.pdf$")

# Recorremos los archivos en la ruta
for filename in os.listdir(local_base_path):
    file_path = os.path.join(local_base_path, filename)

    # Verificar si es un archivo PDF
    if filename.lower().endswith(".pdf"):
        match = pattern.match(filename)

        # Si no cumple el formato o num no es group_to_keep, eliminar el archivo
        if not match or match.group(1) != group_to_keep:
            os.remove(file_path)
            print(f"Eliminado: {filename}")
