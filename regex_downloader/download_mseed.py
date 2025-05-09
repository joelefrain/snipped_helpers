import os
import paramiko

from datetime import datetime, timedelta

# Lista de estaciones
STATIONS = [
    ("AN", "AUDAS", "00", "HN"),
    ("AN", "AUDAS", "01", "HH"),
    ("AN", "RSICA", "00", "EN"),
    ("AN", "RSAQP", "00", "EN"),
    ("AT", "BOTAD", "", "HN"),
    ("AT", "CCAMA", "", "HN"),
    ("AT", "CHABU", "00", "EN"),
    ("RA", "ROCA", "", "HH"),
    ("RA", "SUELO", "", "HH"),
]

ORIENTATION = ["N", "E", "Z"]

def date_range(start_date, end_date):
    current = start_date
    while current <= end_date:
        yield current
        current += timedelta(days=1)

def download_files(sftp, local_base_path, start_date, end_date):
    """Descarga los archivos mseed dentro del rango de fechas especificado."""
    for date in date_range(start_date, end_date):
        year = date.year
        jday = date.timetuple().tm_yday

        for net, sta, loc, model in STATIONS:
            for ori in ORIENTATION:
                filename = f"{net}.{sta}.{loc}.{model}{ori}.D.{year}.{jday:03d}"
                remote_dir = f"/home/sysop/seiscomp/var/lib/archive/{year}/{net}/{sta}/{model}{ori}.D"
                remote_path = f"{remote_dir}/{filename}"

                local_dir = os.path.join(local_base_path, str(year), net, sta)
                os.makedirs(local_dir, exist_ok=True)
                local_path = os.path.join(local_dir, filename)

                try:
                    print(f"Descargando: {remote_path}")
                    sftp.get(remote_path, local_path)
                except FileNotFoundError:
                    print(f"No encontrado: {remote_path}")

if __name__ == "__main__":
    from dotenv import load_dotenv

    # Cargar variables de entorno desde el archivo .env
    load_dotenv()

    # Configuración del servidor desde el archivo .env
    host = os.getenv("SSH_HOST")
    port = os.getenv("SSH_PORT")
    username = os.getenv("SSH_USERNAME")
    password = os.getenv("SSH_PASSWORD")

    local_base_path = 'path/to/local/directory'

    try:
        print("Conectando al servidor...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port=port, username=username, password=password)
        sftp = ssh.open_sftp()

        # Solicitar fechas de consulta al usuario
        start_date_input = input("Ingrese la fecha de inicio (YYYY-MM-DD): ")
        end_date_input = input("Ingrese la fecha de fin (YYYY-MM-DD): ")
        start_date = datetime.strptime(start_date_input, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_input, "%Y-%m-%d")

        print(f"Descargando archivos mseed entre {start_date_input} y {end_date_input}...")
        download_files(sftp, local_base_path, start_date, end_date)

        sftp.close()
        ssh.close()
        print("Descarga completada.")
    except Exception as e:
        print(f"Error: {e}")
