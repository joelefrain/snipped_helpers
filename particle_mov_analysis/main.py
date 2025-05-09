import os
import numpy as np
import matplotlib.pyplot as plt
from obspy import read

class SeismicEventProcessor:
    def __init__(self, archivo_evt):
        self.archivo_evt = archivo_evt
        self.stream = None
        self.traces_data = []
        self.max_values = []

    def leer_archivo(self):
        """Leer el archivo .evt y cargar los datos en un objeto Stream."""
        try:
            self.stream = read(self.archivo_evt, apply_calib=True)
        except Exception as e:
            print(f"Error al leer el archivo .evt: {e}")
            self.stream = None

    def procesar_trazas(self, freqmin=0.02, freqmax=0.2):
        """Procesar las trazas del Stream y almacenar los datos procesados."""
        if not self.stream:
            print("El stream no ha sido cargado correctamente.")
            return

        for trace in self.stream[:6]:  # Procesar solo los primeros 6 canales
            trace.data *= 100  # Convertir a cm/s²
            trace.detrend(type='linear')  # Corrección de tendencia
            trace.filter("bandpass", freqmin=freqmin, freqmax=freqmax)

            # Guardar los datos procesados
            self.traces_data.append(trace.data)

            # Calcular el valor máximo absoluto de la traza
            max_abs_value = np.max(np.abs(trace.data))
            self.max_values.append(max_abs_value)

    def graficar_trazas(self, output_dir):
        """Generar gráficos para cada traza."""
        if not self.traces_data:
            print("No hay datos procesados para graficar.")
            return

        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        axes = axes.flatten()

        for i, trace in enumerate(self.stream[:6]):
            ax = axes[i]
            ax.plot(trace.times(), trace.data, label=f"{trace.stats.channel}")
            ax.set_xlabel("Tiempo (s)")
            ax.set_ylabel("Aceleración (cm/s²)")
            ax.set_title(f"Componente {trace.stats.channel} {self.archivo_evt}")
            ax.legend()

            # Agregar texto con el valor máximo absoluto
            max_abs_value = self.max_values[i]
            ax.text(0.95, 0.9, f"Máx. abs: {max_abs_value:.2f} cm/s²",
                    transform=ax.transAxes, ha='right', fontsize=10,
                    bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray'))

        plt.tight_layout()

        # Guardar el gráfico
        output_svg = os.path.join(output_dir, os.path.basename(self.archivo_evt).replace('.evt', '_subplots.svg'))
        plt.savefig(output_svg)
        print(f"Subplots guardados en: {output_svg}")

    def graficar_orbitas(self, output_dir):
        """Graficar las órbitas de aceleraciones."""
        if len(self.traces_data) < 6:
            print("No hay suficientes datos para graficar órbitas.")
            return

        fig_orbit, axes_orbit = plt.subplots(1, 2, subplot_kw={'projection': 'polar'}, figsize=(12, 6))

        # Primera órbita
        x1, y1 = self.traces_data[0], self.traces_data[1]
        r1 = np.sqrt(x1**2 + y1**2)
        theta1 = np.arctan2(y1, x1)
        max_orbit1 = np.max(r1)
        
        axes_orbit[0].plot(theta1, r1, label="Órbita 1")
        axes_orbit[0].set_title(f"Órbita de aceleraciones (Canal 3 EO vs NS) {self.archivo_evt}")
        axes_orbit[0].text(0.5, 1.05, f"Máx: {max_orbit1:.2f} cm/s²",
                           transform=axes_orbit[0].transAxes, ha='center', fontsize=10,
                           bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray'))

        # Segunda órbita
        x2, y2 = self.traces_data[3], self.traces_data[4]
        r2 = np.sqrt(x2**2 + y2**2)
        theta2 = np.arctan2(y2, x2)
        max_orbit2 = np.max(r2)

        axes_orbit[1].plot(theta2, r2, label="Órbita 2")
        axes_orbit[1].set_title("Órbita de aceleraciones (Canal 6 EO vs NS)")
        axes_orbit[1].text(0.5, 1.05, f"Máx: {max_orbit2:.2f} cm/s²",
                           transform=axes_orbit[1].transAxes, ha='center', fontsize=10,
                           bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray'))

        plt.tight_layout()

        # Guardar las órbitas como archivo SVG
        output_orbit_svg = os.path.join(output_dir, os.path.basename(self.archivo_evt).replace('.evt', '_orbits.svg'))
        plt.savefig(output_orbit_svg)
        print(f"Órbitas guardadas en: {output_orbit_svg}")