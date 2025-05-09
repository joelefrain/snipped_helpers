import os
import re
import glob
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import html

# Configuración de directorios
REPORTS_DIR = "var/reports"
PLOTS_DIR = "var/plots"
COMBINED_DIR = "var/combined"

# Asegurar que el directorio de salida exista
os.makedirs(COMBINED_DIR, exist_ok=True)

def extract_html_content(html_file):
    """Extrae el contenido HTML manteniendo su formato."""
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Usar parser más preciso para preservar estructura
    soup = BeautifulSoup(html_content, 'lxml')
    
    # Extraer todo el contenido dentro de body
    body_content = soup.find('body')
    if body_content:
        # Extraer todos los estilos incluyendo múltiples tags
        style_tags = soup.find_all('style')
        style_content = '\n'.join([tag.string for tag in style_tags if tag.string])
        
        # Preservar estructura HTML completa
        return {
            'content': html.unescape(str(body_content)),
            'style': style_content + '\n' + html.unescape(soup.html['style']) if soup.html and soup.html.has_attr('style') else style_content
        }
    return None

def modify_svg_with_html(svg_file, html_content, svg_width_ratio=1.0, html_width_ratio=0.5):
    """Modifica el SVG para incluir el contenido HTML.
    
    Args:
        svg_file (str): Ruta al archivo SVG.
        html_content (dict): Contenido HTML y estilos.
        svg_width_ratio (float): Ratio para ajustar el ancho del SVG (default: 1.0).
        html_width_ratio (float): Ratio para ajustar el ancho del HTML (default: 0.5).
    """
    with open(svg_file, 'r', encoding='utf-8') as f:
        svg_content = f.read()
    
    # Crear un namespace para SVG
    ET.register_namespace('', "http://www.w3.org/2000/svg")
    ET.register_namespace('xlink', "http://www.w3.org/1999/xlink")
    
    # Parsear el SVG
    svg_tree = ET.fromstring(svg_content)
    
    # Obtener las dimensiones originales del SVG
    width = svg_tree.get('width')
    height = svg_tree.get('height')
    viewBox = svg_tree.get('viewBox')
    
    # Convertir pt a px si es necesario
    if width.endswith('pt'):
        width = float(width[:-2]) * 1.33333
    else:
        width = float(width)
    
    if height.endswith('pt'):
        height = float(height[:-2]) * 1.33333
    else:
        height = float(height)
    
    # Ajustar el viewBox para incluir el HTML
    if viewBox:
        vb_parts = viewBox.split()
        vb_width = float(vb_parts[2])
        vb_height = float(vb_parts[3])
        
        # Nuevo viewBox con espacio para el HTML según ratios especificados
        new_vb_width = vb_width * (svg_width_ratio + html_width_ratio)
        html_width = vb_width * html_width_ratio
        new_viewBox = f"{vb_parts[0]} {vb_parts[1]} {new_vb_width} {vb_height}"
        svg_tree.set('viewBox', new_viewBox)
    
    # Ajustar dimensiones según lo especificado
    svg_tree.set('width', '100%')
    svg_tree.set('height', '100%')
    
    # Crear un elemento extranjero para el HTML
    foreign_object = ET.Element('{http://www.w3.org/2000/svg}foreignObject')
    foreign_object.set('x', str(vb_width))
    foreign_object.set('y', '0')
    foreign_object.set('width', str(vb_width * 0.5))
    foreign_object.set('height', str(vb_height))
    
    # Crear un div para contener el HTML
    div = ET.Element('div')
    div.set('xmlns', 'http://www.w3.org/1999/xhtml')
    div.set('style', 'width: 100%; height: 100%; overflow: auto;')
    
    # Agregar el estilo CSS
    style = ET.Element('style')
    style.text = html_content['style']
    div.append(style)
    
    # Agregar el contenido HTML
    # Necesitamos usar un enfoque diferente ya que ET no maneja bien HTML complejo
    html_str = f"<![CDATA[{html_content['content']}]]>"
    
    # Insertar HTML como CDATA válido
    html_content_str = BeautifulSoup(html_content['content'], 'html.parser').prettify()
    cdata = f'<![CDATA[\n{html_content_str}\n]]>'
    # Convertir el HTML a elementos XML y agregarlos
    html_soup = BeautifulSoup(html_content['content'], 'html.parser')
    # Insertar HTML como CDATA para preservar estructura original
    html_str = f"<![CDATA[{html_content['content']}]]>"
    div.append(ET.fromstring(f'<div xmlns="http://www.w3.org/1999/xhtml">{html_content["content"]}</div>'))
    # Registrar namespaces adicionales
    ET.register_namespace('xhtml', "http://www.w3.org/1999/xhtml")
    
    foreign_object.append(div)
    svg_tree.append(foreign_object)
    
    # Convertir de vuelta a string
    svg_string = ET.tostring(svg_tree, encoding='unicode')
    
    # Reemplazar el CDATA por el HTML real (sin los comentarios)
    svg_string = svg_string.replace('&lt;![CDATA[', '<![CDATA[')
    svg_string = svg_string.replace(']]&gt;', ']]>')
    # Mantener los bloques CDATA intactos
    svg_string = svg_string.replace('&lt;![CDATA[', '<![CDATA[')
    svg_string = svg_string.replace(']]&gt;', ']]>')
    
    return svg_string

def process_files(svg_width_ratio=1.0, html_width_ratio=0.5):
    """Procesa todos los archivos HTML y SVG relacionados.
    
    Args:
        svg_width_ratio (float): Ratio para ajustar el ancho del SVG (default: 1.0).
        html_width_ratio (float): Ratio para ajustar el ancho del HTML (default: 0.5).
    """
    # Obtener todos los archivos HTML en la carpeta de reportes
    html_files = glob.glob(os.path.join(REPORTS_DIR, "analysis_*.html"))
    
    for html_file in html_files:
        # Extraer el nombre base (ej: analysis_PCT-01_GC_HOR)
        base_name = os.path.basename(html_file)
        name_without_ext = os.path.splitext(base_name)[0]
        series_id = name_without_ext.replace('analysis_', '')
        
        # Buscar los archivos SVG correspondientes
        decomp_svg = os.path.join(PLOTS_DIR, f"decomposition_{series_id}.svg")
        forecast_svg = os.path.join(PLOTS_DIR, f"forecast_{series_id}.svg")
        
        # Procesar el archivo de descomposición si existe
        if os.path.exists(decomp_svg):
            html_content = extract_html_content(html_file)
            if html_content:
                combined_svg = modify_svg_with_html(decomp_svg, html_content, svg_width_ratio, html_width_ratio)
                output_file = os.path.join(COMBINED_DIR, base_name.replace('.html', '.svg'))
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(combined_svg)
                print(f"Creado: {output_file}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Combina archivos SVG y HTML con dimensiones personalizables.')
    parser.add_argument('--svg-width', type=float, default=1.0,
                        help='Ratio para ajustar el ancho del SVG (default: 1.0)')
    parser.add_argument('--html-width', type=float, default=0.5,
                        help='Ratio para ajustar el ancho del HTML (default: 0.5)')
    
    args = parser.parse_args()
    process_files(args.svg_width, args.html_width)
    print("Proceso completado.")