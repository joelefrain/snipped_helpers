import os
import shutil


def move_files(local_base_path):
    """Mueve todos los archivos .txt de las subcarpetas a la carpeta base."""
    for root, _, files in os.walk(local_base_path):
        if root == local_base_path:
            continue  # Evita procesar la carpeta base
        
        for file in files:
            if file.endswith(".txt"):
                origen = os.path.join(root, file)
                destino = os.path.join(local_base_path, file)
                
                # Si el archivo ya existe, agregar un sufijo para evitar sobrescribir
                contador = 1
                while os.path.exists(destino):
                    nombre, extension = os.path.splitext(file)
                    destino = os.path.join(local_base_path, f"{nombre}_{contador}{extension}")
                    contador += 1
                
                try:
                    shutil.move(origen, destino)
                    print(f"Movido: {origen} → {destino}")
                except Exception as e:
                    print(f"Error al mover {file}: {e}")

if __name__ == "__main__":

    # Ruta base donde están las subcarpetas con los archivos .txt
    local_base_path = "path/to/your/local/base/path"
    move_files(local_base_path)
