import os
import csv


def generate_directory_csv(directory, output_csv):
    # Lista para almacenar los datos del CSV
    rows = []

    # Función recursiva para recorrer el directorio
    def walk_directory(current_path, prefix=""):
        # Procesa archivos y carpetas
        items = sorted(os.listdir(current_path))

        for i, item in enumerate(items):
            item_path = os.path.join(current_path, item)
            is_last = i == len(items) - 1  # Verifica si es el último elemento

            # Formato de prefijo para el árbol
            tree_prefix = f"{prefix}{'└── ' if is_last else '├── '}{item}"

            # Calcula el tamaño del archivo (en KB), si es un archivo
            size = os.path.getsize(item_path) / \
                1024 if os.path.isfile(item_path) else "-"

            # Obtiene la extensión del archivo y el tipo
            if os.path.isfile(item_path):
                extension = os.path.splitext(item)[1] or "Sin extensión"
                file_type = "Archivo"
            else:
                extension = "-"
                file_type = "Carpeta"

            # Guarda en la lista el nombre, la ruta, el tamaño, la extensión y el tipo
            rows.append([tree_prefix, item_path, size, extension, file_type])

            # Define el nuevo prefijo para los elementos anidados
            new_prefix = f"{prefix}{'    ' if is_last else '│   '}"

            # Llamada recursiva para subdirectorios
            if os.path.isdir(item_path):
                walk_directory(item_path, new_prefix)

    # Inicia el recorrido del directorio en el nivel raíz
    walk_directory(directory)

    # Escribe los datos en un archivo CSV con separador de punto y coma
    with open(output_csv, mode='w', newline='', encoding='utf-8-sig') as csv_file:
        writer = csv.writer(csv_file, delimiter=';')
        # Encabezados del CSV
        writer.writerow(['nombre', 'ruta', 'peso (KB)', 'extensión', 'tipo'])
        writer.writerows(rows)

    print(f"CSV generado en: {output_csv}")

if __name__ == "__main__":
    
    directory = 'path/to/your/directory'  # Cambia esto por la ruta de tu directorio
    output_csv = 'output.csv'  # Cambia esto por la ruta de tu archivo CSV de salida
    generate_directory_csv(directory, output_csv)
