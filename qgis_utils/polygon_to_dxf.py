import os
import ezdxf
from shapely.geometry import LineString, Polygon
from shapely.ops import split

# Función para convertir una polilínea DXF en una geometría Shapely (LineString)
def polyline_to_linestring(polyline):
    points = [(point[0], point[1]) for point in polyline.points()]
    return LineString(points)

# Función para procesar cada polígono y crear un DXF con las polilíneas cortadas
def crear_dxf_por_poligono(dxf_path, output_folder):
    # Crear la carpeta de salida si no existe
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Cargar el archivo DXF
    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()

    # Extraer las polilíneas de la capa "lineas" y los polígonos de la capa "poligonos"
    lineas = [e for e in msp.query('LWPOLYLINE') if e.dxf.layer == 'lineas']
    poligonos = [e for e in msp.query('LWPOLYLINE') if e.dxf.layer == 'poligonos' and e.closed]

    for i, poligono_entity in enumerate(poligonos):
        # Convertir el polígono en una geometría Shapely (Polygon)
        poligono_geom = Polygon(polyline_to_linestring(poligono_entity).coords)

        # Crear un nuevo archivo DXF para este polígono
        new_doc = ezdxf.new(dxfversion="R2010")
        new_msp = new_doc.modelspace()

        # Procesar cada polilínea y recortarla
        for linea_entity in lineas:
            linea_geom = polyline_to_linestring(linea_entity)
            
            # Intersección entre la polilínea y el polígono
            interseccion = poligono_geom.intersection(linea_geom)

            # Si hay intersección, agregar los segmentos al nuevo DXF
            if not interseccion.is_empty:
                # Convertir la geometría de intersección en una polilínea DXF
                if isinstance(interseccion, LineString):
                    puntos = list(interseccion.coords)
                    new_polyline = new_msp.add_lwpolyline(puntos)
                    new_polyline.dxf.layer = 'lineas'
                elif interseccion.geom_type == 'MultiLineString':
                    for line in interseccion:
                        puntos = list(line.coords)
                        new_polyline = new_msp.add_lwpolyline(puntos)
                        new_polyline.dxf.layer = 'lineas'

        # Guardar el archivo DXF individual en la carpeta de salida
        output_path = os.path.join(output_folder, f"poligono_{i+1}.dxf")
        new_doc.saveas(output_path)
        print(f"Archivo '{output_path}' creado.")


carpeta_salida = "output"
ruta_dxf = r'C:\Users\joel.alarcon\Downloads\FUENTES\ACAD-l-intraslab.dxf'
crear_dxf_por_poligono(ruta_dxf, carpeta_salida)
