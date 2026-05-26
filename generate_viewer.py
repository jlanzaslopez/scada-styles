#!/usr/bin/env python3
"""
generate_viewer.py — Genera styles_data_<NAME>.js + styles_index.json
                     a partir de los XMLs de estilos de AVEVA System Platform.

Modos de uso:
    # Un solo XML
    python generate_viewer.py styles/Standard_Style.xml docs/

    # Todos los XMLs de una carpeta (modo --all)
    python generate_viewer.py --all styles/ docs/

Genera en docs/:
    styles_data_<NAME>.js   — datos de cada XML
    styles_index.json        — lista de XMLs disponibles

No tiene dependencias externas — solo Python 3 stdlib.
"""

import sys
import json
import os
import glob
import xml.etree.ElementTree as ET


# ──────────────────────────────────────────────────────────────────────────────
# CATEGORY MAPPING
# ──────────────────────────────────────────────────────────────────────────────
CATEGORIES = {
    10: ('HMI', 'Texto base'), 20: ('HMI', 'Texto base'), 30: ('HMI', 'Texto base'),
    35: ('HMI', 'Texto base'), 40: ('HMI', 'Texto base'), 50: ('HMI', 'Texto base'),
    60: ('HMI', 'Texto base'),
    70:  ('HMI', 'Estados de equipo'), 77:  ('HMI', 'Estados de equipo'),
    80:  ('HMI', 'Estados de equipo'), 83:  ('HMI', 'Estados de equipo'),
    85:  ('HMI', 'Estados de equipo'), 90:  ('HMI', 'Estados de equipo'),
    100: ('HMI', 'Estados de equipo'),
    110: ('HMI', 'Valores de proceso'), 120: ('HMI', 'Valores de proceso'),
    130: ('HMI', 'Valores de proceso'), 140: ('HMI', 'Valores de proceso'),
    150: ('HMI', 'Valores de proceso'), 160: ('HMI', 'Valores de proceso'),
    165: ('HMI', 'Valores de proceso'), 270: ('HMI', 'Valores de proceso'),
    170: ('HMI', 'Líneas de proceso'), 180: ('HMI', 'Líneas de proceso'),
    190: ('HMI', 'Líneas de proceso'),
    200: ('HMI', 'Modos de control'), 210: ('HMI', 'Modos de control'),
    215: ('HMI', 'Modos de control'),
    220: ('HMI', 'Vallado/contenedores'), 230: ('HMI', 'Vallado/contenedores'),
    250: ('HMI', 'Límites de desviación'), 260: ('HMI', 'Límites de desviación'),
    263: ('HMI', 'Sistema de seguridad'),
    265: ('HMI', 'Medidores y trackers'), 275: ('HMI', 'Medidores y trackers'),
    1040: ('HMI', 'Medidores y trackers'),
    277: ('HMI', 'Direcciones y navegación'), 278: ('HMI', 'Direcciones y navegación'),
    480: ('HMI', 'Calidad'), 484: ('HMI', 'Calidad'), 488: ('HMI', 'Calidad'),
    501: ('HMI', 'Intensidades de gris'), 502: ('HMI', 'Intensidades de gris'),
    503: ('HMI', 'Intensidades de gris'), 504: ('HMI', 'Intensidades de gris'),
    505: ('HMI', 'Intensidades de gris'), 506: ('HMI', 'Intensidades de gris'),
    570: ('HMI', 'Defaults del sistema'), 580: ('HMI', 'Defaults del sistema'),
    590: ('HMI', 'Defaults del sistema'), 600: ('HMI', 'Defaults del sistema'),
    610: ('HMI', 'Defaults del sistema'), 620: ('HMI', 'Defaults del sistema'),
    630: ('HMI', 'Defaults del sistema'), 640: ('HMI', 'Defaults del sistema'),
    280: ('Alarm', 'Fondo UNACK'),  290: ('Alarm', 'Fondo UNACK'),
    300: ('Alarm', 'Fondo UNACK'),  310: ('Alarm', 'Fondo UNACK'),
    320: ('Alarm', 'Fondo ACK'),    330: ('Alarm', 'Fondo ACK'),
    340: ('Alarm', 'Fondo ACK'),    350: ('Alarm', 'Fondo ACK'),
    360: ('Alarm', 'Fondo RTN'),    370: ('Alarm', 'Fondo RTN'),
    380: ('Alarm', 'Fondo RTN'),    390: ('Alarm', 'Fondo RTN'),
    400: ('Alarm', 'Estados especiales'), 410: ('Alarm', 'Estados especiales'),
    420: ('Alarm', 'Estados especiales'),
    1050: ('Alarm', 'Borde UNACK'), 1060: ('Alarm', 'Borde UNACK'),
    1070: ('Alarm', 'Borde UNACK'), 1080: ('Alarm', 'Borde UNACK'),
    1090: ('Alarm', 'Borde ACK'),   1100: ('Alarm', 'Borde ACK'),
    1110: ('Alarm', 'Borde ACK'),   1120: ('Alarm', 'Borde ACK'),
    1130: ('Alarm', 'Borde RTN'),   1140: ('Alarm', 'Borde RTN'),
    1150: ('Alarm', 'Borde RTN'),   1160: ('Alarm', 'Borde RTN'),
    1170: ('Alarm', 'Borde estados'), 1180: ('Alarm', 'Borde estados'),
    1190: ('Alarm', 'Borde estados'), 1200: ('Alarm', 'Borde estados'),
}
for _id in range(800, 1031, 10):
    CATEGORIES[_id] = ('UserDefined', 'Disponibles')

USAGE_DESCRIPTIONS = {
    110: 'Valor mediano (default KPIs)', 130: 'Valor mediano regular (secundario)',
    140: 'Valor pequeño (tablas, info densa)', 270: 'Valor grande (KPIs destacados)',
    120: 'No aplica en agua/saneamiento', 150: 'No aplica en agua/saneamiento',
    160: 'No aplica en agua/saneamiento', 165: 'No aplica en agua/saneamiento',
    10: 'Título de pantalla', 20: 'Subtítulo de sección', 30: 'Etiqueta general',
    35: 'Texto descriptivo pequeño', 40: 'Nombre de tag/instrumento',
    50: 'Unidades de ingeniería', 60: 'Color de fondo de pantalla',
    200: 'Modo automático', 210: 'Modo manual', 215: 'Modo cascada',
    220: 'Tarjeta blanca con línea gris', 230: 'Tarjeta de contraste',
    263: 'Banner de seguridad crítica',
    480: 'Calidad: buena', 484: 'Calidad: aceptable', 488: 'Calidad: mala',
    278: 'Botones de navegación',
}

SAMPLE_TEXT_BY_NAME = {
    'Title': 'Título de pantalla', 'Heading': 'Subtítulo', 'Label': 'Etiqueta',
    'Descriptor': 'descripción larga', 'Tagname': 'PUMP_001',
    'Engineering_Units': 'm³/h', 'Actual_Value': '142.53', 'Setpoint': '150.00',
    'Recent_Value_Range': '098.40 — 215.70', 'Tracker': '142.53',
    'Control_Mode_Automatic': 'AUTO', 'Control_Mode_Manual': 'MAN',
    'Control_Mode_Cascade': 'CAS', 'Fencing_1': '', 'Fencing_2': '',
    'SafetySystem': 'EMERGENCY STOP', 'Navigation': 'Navegar',
    'Good': 'GOOD', 'Satisfactory': 'OK', 'Bad': 'BAD',
    'Default_FontFamily': 'Aa Bb Cc 123', 'Default_FontStyle': 'Aa Bb Cc 123',
}


# ──────────────────────────────────────────────────────────────────────────────
# XML PARSING
# ──────────────────────────────────────────────────────────────────────────────
def parse_color(color_elem):
    if color_elem is None: return None
    fill_type = color_elem.get('FillType', 'Solid')
    if fill_type == 'Solid':
        sf = color_elem.find('SolidFill')
        if sf is None: return None
        fc = sf.find('FillColor')
        trans_elem = sf.find('Transparency')
        trans = int(trans_elem.text) if trans_elem is not None else 0
        if fc is None: return None
        r, g, b, a = int(fc.get('R')), int(fc.get('G')), int(fc.get('B')), int(fc.get('A'))
        alpha_final = a / 255 * (1 - trans / 100)
        css = f'rgba({r},{g},{b},{alpha_final:.3f})' if (trans > 0 or a < 255) else f'rgb({r},{g},{b})'
        return {'type': 'solid', 'r': r, 'g': g, 'b': b, 'a': a, 'transparency': trans, 'css': css}
    elif fill_type == 'Pattern':
        pf = color_elem.find('PatternFill')
        if pf is None: return None
        bc, fc = pf.find('BackColor'), pf.find('ForeColor')
        hatch = pf.find('HatchStyle')
        return {
            'type': 'pattern',
            'back': f'rgb({bc.get("R")},{bc.get("G")},{bc.get("B")})' if bc is not None else 'transparent',
            'fore': f'rgb({fc.get("R")},{fc.get("G")},{fc.get("B")})' if fc is not None else 'black',
            'hatch': hatch.text if hatch is not None else 'DiagonalCross',
        }
    return None

def parse_blink(parent):
    blink = parent.find('Blink')
    if blink is None: return None
    return {'speed': blink.get('Speed', 'Slow'), 'color': parse_color(blink.find('Color'))}

def is_forced_text(ts):
    return ts is not None and (ts.find('Font') is not None or ts.find('Color') is not None)

def is_forced_fill(fs):
    if fs is None: return False
    c = fs.find('Color')
    if c is None: return False
    p = parse_color(c)
    return p is not None and (p['type'] == 'pattern' or p.get('transparency', 0) < 100)

def is_forced_line(ls):
    if ls is None: return False
    c = ls.find('Color')
    if c is None: return False
    p = parse_color(c)
    return p is not None and (p['type'] == 'pattern' or p.get('transparency', 0) < 100)

def parse_es(es):
    es_id = int(es.get('Id'))
    if es_id not in CATEGORIES: return None
    cat, subgroup = CATEGORIES[es_id]
    name = es.get('Name')
    gp = es.find('GraphicPrimitive')
    if gp is None: return None
    ts, fs, ls = gp.find('TextStyle'), gp.find('FillStyle'), gp.find('LineStyle')
    outline = es.find('Outline')
    text_data = {'forced': is_forced_text(ts)}
    if text_data['forced']:
        font = ts.find('Font')
        if font is not None:
            text_data.update({'font': font.get('Name'), 'size': float(font.get('Size')),
                              'bold': font.get('Bold') == 'true', 'italic': font.get('Italic') == 'true'})
        c = ts.find('Color')
        if c is not None: text_data['color'] = parse_color(c)
        text_data['blink'] = parse_blink(ts)
    fill_data = {'forced': is_forced_fill(fs)}
    if fill_data['forced']:
        fill_data['color'] = parse_color(fs.find('Color'))
        fill_data['blink'] = parse_blink(fs)
    line_data = {'forced': is_forced_line(ls)}
    if line_data['forced']:
        line_data.update({'pattern': ls.get('Pattern', 'Solid'), 'weight': float(ls.get('Weight', '1')),
                          'color': parse_color(ls.find('Color')), 'blink': parse_blink(ls)})
    outline_data = {'forced': False}
    if outline is not None and outline.get('Enabled') == 'true':
        outline_data['forced'] = True
        line = outline.find('Line')
        if line is not None:
            outline_data.update({'pattern': line.get('Pattern', 'Solid'), 'weight': float(line.get('Weight', '1')),
                                  'color': parse_color(line.find('Color'))})
        outline_data['blink'] = parse_blink(outline)
    return {'id': es_id, 'name': name, 'category': cat, 'subgroup': subgroup,
            'usage': USAGE_DESCRIPTIONS.get(es_id, ''),
            'text': text_data, 'fill': fill_data, 'line': line_data, 'outline': outline_data}

def parse_xml(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    styles = [s for es in root.findall('ES') if (s := parse_es(es))]
    cat_order = {'HMI': 0, 'Alarm': 1, 'UserDefined': 2}
    styles.sort(key=lambda s: (cat_order.get(s['category'], 99), s['id']))
    return styles


# ──────────────────────────────────────────────────────────────────────────────
# OUTPUT
# ──────────────────────────────────────────────────────────────────────────────
def xml_to_key(xml_path):
    """Convert path like styles/Standard_Style.xml → Standard_Style"""
    return os.path.splitext(os.path.basename(xml_path))[0]

def generate_one(xml_path, output_dir):
    key = xml_to_key(xml_path)
    styles = parse_xml(xml_path)
    out_path = os.path.join(output_dir, f'styles_data_{key}.json')
    payload = {'styles': styles, 'sample_text': SAMPLE_TEXT_BY_NAME}
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False)
    print(f'  ✅  {out_path} ({len(styles)} styles)')
    return key

def generate_all(styles_dir, output_dir):
    xmls = sorted(glob.glob(os.path.join(styles_dir, '*.xml')))
    if not xmls:
        print(f'No XML files found in {styles_dir}')
        sys.exit(1)
    keys = []
    for xml_path in xmls:
        key = generate_one(xml_path, output_dir)
        keys.append({'key': key, 'file': os.path.basename(xml_path)})
    index_path = os.path.join(output_dir, 'styles_index.json')
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(keys, f, ensure_ascii=False, indent=2)
    print(f'  ✅  {index_path} ({len(keys)} entries)')

def main():
    if len(sys.argv) == 4 and sys.argv[1] == '--all':
        generate_all(sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 3:
        key = generate_one(sys.argv[1], sys.argv[2])
        index_path = os.path.join(sys.argv[2], 'styles_index.json')
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump([{'key': key, 'file': os.path.basename(sys.argv[1])}], f)
        print(f'  ✅  {index_path}')
    else:
        print(__doc__)
        sys.exit(1)

if __name__ == '__main__':
    main()
