import os
import paramiko

from scp import SCPClient


def create_ssh_client(host, port, username, password):
    """Crea un cliente SSH y lo conecta al servidor."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, port, username, password)
    return client


def get_folders_by_date(ssh_client, remote_base_path, start_date, end_date):
    """Obtiene las subcarpetas creadas entre las fechas especificadas."""
    command = f"find {remote_base_path} -mindepth 1 -maxdepth 1 -type d -newermt '{start_date}' ! -newermt '{end_date}'"

    stdin, stdout, stderr = ssh_client.exec_command(command)
    folder_list = stdout.read().decode().splitlines()

    return folder_list


def get_txt_files(ssh_client, folder, network_code):
    """Obtiene la lista de archivos .txt que cumplen con el criterio dentro de la carpeta."""
    command = (
        f"find {folder} -type f -name 'RED_{network_code}*.txt' "
        f"! -name '*g.txt' ! -name '*mg.txt' ! -name '*m.txt'"
    )

    _, stdout, _ = ssh_client.exec_command(command)
    file_list = stdout.read().decode().splitlines()

    return file_list


def download_files(ssh_client, files, local_base_path):
    """Descarga los archivos seleccionados."""
    with SCPClient(ssh_client.get_transport()) as scp:
        for remote_file in files:
            # Determinar la carpeta donde guardar el archivo en local
            relative_path = os.path.relpath(remote_file, remote_base_path)
            local_file_path = os.path.join(local_base_path, relative_path)

            # Crear la carpeta si no existe
            os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

            print(f"Descargando {remote_file} a {local_file_path}...")
            scp.get(remote_file, local_file_path)


if __name__ == "__main__":
    from dotenv import load_dotenv

    # Cargar variables de entorno desde el archivo .env
    load_dotenv()

    # Configuración del servidor desde el archivo .env
    host = os.getenv("SSH_HOST")
    port = os.getenv("SSH_PORT")
    username = os.getenv("SSH_USERNAME")
    password = os.getenv("SSH_PASSWORD")

    # Ruta en el servidor
    remote_base_path = "/var/www/html/sensor/events/"
    # Ruta local
    local_base_path = "path/to/local/directory"

    try:
        print("Conectando al servidor...")
        ssh = create_ssh_client(host, port, username, password)

        # Solicitar fechas de consulta al usuario
        start_date = input("Ingrese la fecha de inicio (YYYY-MM-DD): ")
        end_date = input("Ingrese la fecha de fin (YYYY-MM-DD): ")

        # Solicitar el valor de 'RA' al usuario
        network_code = input("Ingrese el valor para el código de red: ")

        print(f"Buscando carpetas creadas entre {start_date} y {end_date}...")
        folders_to_download = get_folders_by_date(
            ssh, remote_base_path, start_date, end_date
        )

        if folders_to_download:
            print(
                f"Se encontraron {len(folders_to_download)} carpetas. Buscando archivos..."
            )

            all_files = []
            for folder in folders_to_download:
                txt_files = get_txt_files(ssh, folder, network_code)
                all_files.extend(txt_files)

            if all_files:
                print(
                    f"Se encontraron {len(all_files)} archivos .txt que cumplen con los criterios. Iniciando descarga..."
                )
                download_files(ssh, all_files, local_base_path)
                print("Descarga completada.")
            else:
                print(
                    "No se encontraron archivos .txt con los criterios especificados."
                )

        else:
            print("No se encontraron carpetas en el rango de fechas especificado.")

        ssh.close()
    except Exception as e:
        print(f"Error: {e}")
