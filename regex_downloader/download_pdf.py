import os
import paramiko

from scp import SCPClient


def create_ssh_client(host, port, username, password):
    """Crea un cliente SSH y lo conecta al servidor."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, port, username, password)
    return client


def get_pdf_files(ssh_client, remote_base_path, start_date, end_date):
    """Obtiene la lista de archivos PDF en la carpeta base dentro del rango de fechas."""
    command = (
        f"find {remote_base_path} -maxdepth 1 -type f -name '*.pdf' "
        f"-newermt '{start_date}' ! -newermt '{end_date}'"
    )
    stdin, stdout, stderr = ssh_client.exec_command(command)
    file_list = stdout.read().decode().splitlines()
    return file_list


def download_files(ssh_client, files, local_base_path):
    """Descarga los archivos seleccionados."""
    with SCPClient(ssh_client.get_transport()) as scp:
        for remote_file in files:
            local_file_path = os.path.join(
                local_base_path, os.path.basename(remote_file)
            )
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

        print(f"Buscando archivos PDF creados entre {start_date} y {end_date}...")
        pdf_files = get_pdf_files(ssh, remote_base_path, start_date, end_date)

        if pdf_files:
            print(
                f"Se encontraron {len(pdf_files)} archivos PDF. Iniciando descarga..."
            )
            download_files(ssh, pdf_files, local_base_path)
            print("Descarga completada.")
        else:
            print("No se encontraron archivos PDF en el rango de fechas especificado.")

        ssh.close()
    except Exception as e:
        print(f"Error: {e}")
