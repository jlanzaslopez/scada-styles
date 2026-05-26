#!/usr/bin/env python3
"""
generate_viewer.py — Genera styles_data.js a partir de un XML de estilos de
                     AVEVA System Platform.

Uso:
    python generate_viewer.py <input.xml> <output_dir>
    python generate_viewer.py styles/Standard_Style.xml docs/

El script solo escribe docs/styles_data.js con los datos parseados.
El HTML/CSS/JS del visor son ficheros estáticos en docs/ que no se tocan.

No tiene dependencias externas — solo Python 3 stdlib.
"""

import sys
import json
import xml.etree.ElementTree as ET


# ──────────────────────────────────────────────────────────────────────────────
# CATEGORY MAPPING
# Maps each ES Id to (category, subgroup).
# ──────────────────────────────────────────────────────────────────────────────
CATEGORIES = {
    # ─── HMI Element ───
    10: ('HMI', 'Texto base'),
    20: ('HMI', 'Texto base'),
    30: ('HMI', 'Texto base'),
    35: ('HMI', 'Texto base'),
    40: ('HMI', 'Texto base'),
    50: ('HMI', 'Texto base'),
    60: ('HMI', 'Texto base'),
    70:  ('HMI', 'Estados de equipo'),
    77:  ('HMI', 'Estados de equipo'),
    80:  ('HMI', 'Estados de equipo'),
    83:  ('HMI', 'Estados de equipo'),
    85:  ('HMI', 'Estados de equipo'),
    90:  ('HMI', 'Estados de equipo'),
    100: ('HMI', 'Estados de equipo'),
    110: ('HMI', 'Valores de proceso'),
    120: ('HMI', 'Valores de proceso'),
    130: ('HMI', 'Valores de proceso'),
    140: ('HMI', 'Valores de proceso'),
    150: ('HMI', 'Valores de proceso'),
    160: ('HMI', 'Valores de proceso'),
    165: ('HMI', 'Valores de proceso'),
    270: ('HMI', 'Valores de proceso'),
    170: ('HMI', 'Líneas de proceso'),
    180: ('HMI', 'Líneas de proceso'),
    190: ('HMI', 'Líneas de proceso'),
    200: ('HMI', 'Modos de control'),
    210: ('HMI', 'Modos de control'),
    215: ('HMI', 'Modos de control'),
    220: ('HMI', 'Vallado/contenedores'),
    230: ('HMI', 'Vallado/contenedores'),
    250: ('HMI', 'Límites de desviación'),
    260: ('HMI', 'Límites de desviación'),
    263: ('HMI', 'Sistema de seguridad'),
    265:  ('HMI', 'Medidores y trackers'),
    275:  ('HMI', 'Medidores y trackers'),
    1040: ('HMI', 'Medidores y trackers'),
    277: ('HMI', 'Direcciones y navegación'),
    278: ('HMI', 'Direcciones y navegación'),
    480: ('HMI', 'Calidad'),
    484: ('HMI', 'Calidad'),
    488: ('HMI', 'Calidad'),
    501: ('HMI', 'Intensidades de gris'),
    502: ('HMI', 'Intensidades de gris'),
    503: ('HMI', 'Intensidades de gris'),
    504: ('HMI', 'Intensidades de gris'),
    505: ('HMI', 'Intensidades de gris'),
    506: ('HMI', 'Intensidades de gris'),
    570: ('HMI', 'Defaults del sistema'),
    580: ('HMI', 'Defaults del sistema'),
    590: ('HMI', 'Defaults del sistema'),
    600: ('HMI', 'Defaults del sistema'),
    610: ('HMI', 'Defaults del sistema'),
    620: ('HMI', 'Defaults del sistema'),
    630: ('HMI', 'Defaults del sistema'),
    640: ('HMI', 'Defaults del sistema'),
    # ─── Alarm Element ───
    280: ('Alarm', 'Fondo UNACK'),
    290: ('Alarm', 'Fondo UNACK'),
    300: ('Alarm', 'Fondo UNACK'),
    310: ('Alarm', 'Fondo UNACK'),
    320: ('Alarm', 'Fondo ACK'),
    330: ('Alarm', 'Fondo ACK'),
    340: ('Alarm', 'Fondo ACK'),
    350: ('Alarm', 'Fondo ACK'),
    360: ('Alarm', 'Fondo RTN'),
    370: ('Alarm', 'Fondo RTN'),
    380: ('Alarm', 'Fondo RTN'),
    390: ('Alarm', 'Fondo RTN'),
    400: ('Alarm', 'Estados especiales'),
    410: ('Alarm', 'Estados especiales'),
    420: ('Alarm', 'Estados especiales'),
    1050: ('Alarm', 'Borde UNACK'),
    1060: ('Alarm', 'Borde UNACK'),
    1070: ('Alarm', 'Borde UNACK'),
    1080: ('Alarm', 'Borde UNACK'),
    1090: ('Alarm', 'Borde ACK'),
    1100: ('Alarm', 'Borde ACK'),
    1110: ('Alarm', 'Borde ACK'),
    1120: ('Alarm', 'Borde ACK'),
    1130: ('Alarm', 'Borde RTN'),
    1140: ('Alarm', 'Borde RTN'),
    1150: ('Alarm', 'Borde RTN'),
    1160: ('Alarm', 'Borde RTN'),
    1170: ('Alarm', 'Borde estados'),
    1180: ('Alarm', 'Borde estados'),
    1190: ('Alarm', 'Borde estados'),
    1200: ('Alarm', 'Borde estados'),
}

# User_Defined slots (24 total: Ids 800, 810, ..., 1030)
for _id in range(800, 1031, 10):
    CATEGORIES[_id] = ('UserDefined', 'Disponibles')


# ──────────────────────────────────────────────────────────────────────────────
# USAGE DESCRIPTIONS
# ──────────────────────────────────────────────────────────────────────────────
USAGE_DESCRIPTIONS = {
    110: 'Valor mediano (default KPIs)',
    130: 'Valor mediano regular (secundario)',
    140: 'Valor pequeño (tablas, info densa)',
    270: 'Valor grande (KPIs destacados)',
    120: 'No aplica en agua/saneamiento',
    150: 'No aplica en agua/saneamiento',
    160: 'No aplica en agua/saneamiento',
    165: 'No aplica en agua/saneamiento',
    10: 'Título de pantalla',
    20: 'Subtítulo de sección',
    30: 'Etiqueta general',
    35: 'Texto descriptivo pequeño',
    40: 'Nombre de tag/instrumento',
    50: 'Unidades de ingeniería',
    60: 'Color de fondo de pantalla',
    200: 'Modo automático',
    210: 'Modo manual',
    215: 'Modo cascada',
    220: 'Tarjeta blanca con línea gris',
    230: 'Tarjeta de contraste',
    263: 'Banner de seguridad crítica',
    480: 'Calidad: buena',
    484: 'Calidad: aceptable',
    488: 'Calidad: mala',
    278: 'Botones de navegación',
}


# ──────────────────────────────────────────────────────────────────────────────
# SAMPLE TEXT FOR PREVIEWS
# ──────────────────────────────────────────────────────────────────────────────
SAMPLE_TEXT_BY_NAME = {
    'Title': 'Título de pantalla',
    'Heading': 'Subtítulo',
    'Label': 'Etiqueta',
    'Descriptor': 'descripción larga',
    'Tagname': 'PUMP_001',
    'Engineering_Units': 'm³/h',
    'Actual_Value': '142.53',
    'Setpoint': '150.00',
    'Recent_Value_Range': '098.40 — 215.70',
    'Tracker': '142.53',
    'Control_Mode_Automatic': 'AUTO',
    'Control_Mode_Manual': 'MAN',
    'Control_Mode_Cascade': 'CAS',
    'Fencing_1': '',
    'Fencing_2': '',
    'SafetySystem': 'EMERGENCY STOP',
    'Navigation': 'Navegar',
    'Good': 'GOOD',
    'Satisfactory': 'OK',
    'Bad': 'BAD',
    'Default_FontFamily': 'Aa Bb Cc 123',
    'Default_FontStyle': 'Aa Bb Cc 123',
}


# ──────────────────────────────────────────────────────────────────────────────
# XML PARSING  (unchanged from original)
# ──────────────────────────────────────────────────────────────────────────────

def parse_color(color_elem):
    if color_elem is None:
        return None
    fill_type = color_elem.get('FillType', 'Solid')
    if fill_type == 'Solid':
        sf = color_elem.find('SolidFill')
        if sf is None:
            return None
        fc = sf.find('FillColor')
        trans_elem = sf.find('Transparency')
        trans = int(trans_elem.text) if trans_elem is not None else 0
        if fc is None:
            return None
        r = int(fc.get('R'))
        g = int(fc.get('G'))
        b = int(fc.get('B'))
        a = int(fc.get('A'))
        alpha_final = a / 255 * (1 - trans / 100)
        if trans > 0 or a < 255:
            css = f'rgba({r},{g},{b},{alpha_final:.3f})'
        else:
            css = f'rgb({r},{g},{b})'
        return {'type': 'solid', 'r': r, 'g': g, 'b': b, 'a': a,
                'transparency': trans, 'css': css}
    elif fill_type == 'Pattern':
        pf = color_elem.find('PatternFill')
        if pf is None:
            return None
        bc = pf.find('BackColor')
        fc = pf.find('ForeColor')
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
    if blink is None:
        return None
    return {'speed': blink.get('Speed', 'Slow'), 'color': parse_color(blink.find('Color'))}


def is_forced_text(text_style):
    if text_style is None:
        return False
    return text_style.find('Font') is not None or text_style.find('Color') is not None


def is_forced_fill(fill_style):
    if fill_style is None:
        return False
    color = fill_style.find('Color')
    if color is None:
        return False
    parsed = parse_color(color)
    if parsed is None:
        return False
    if parsed['type'] == 'pattern':
        return True
    return parsed.get('transparency', 0) < 100


def is_forced_line(line_style):
    if line_style is None:
        return False
    color = line_style.find('Color')
    if color is None:
        return False
    parsed = parse_color(color)
    if parsed is None:
        return False
    if parsed['type'] == 'pattern':
        return True
    return parsed.get('transparency', 0) < 100


def parse_es(es):
    es_id = int(es.get('Id'))
    if es_id not in CATEGORIES:
        return None
    cat, subgroup = CATEGORIES[es_id]
    name = es.get('Name')
    gp = es.find('GraphicPrimitive')
    if gp is None:
        return None

    text_style = gp.find('TextStyle')
    fill_style = gp.find('FillStyle')
    line_style = gp.find('LineStyle')
    outline    = es.find('Outline')

    text_data = {'forced': is_forced_text(text_style)}
    if text_data['forced']:
        font = text_style.find('Font')
        if font is not None:
            text_data['font']   = font.get('Name')
            text_data['size']   = float(font.get('Size'))
            text_data['bold']   = font.get('Bold') == 'true'
            text_data['italic'] = font.get('Italic') == 'true'
        color = text_style.find('Color')
        if color is not None:
            text_data['color'] = parse_color(color)
        text_data['blink'] = parse_blink(text_style)

    fill_data = {'forced': is_forced_fill(fill_style)}
    if fill_data['forced']:
        fill_data['color'] = parse_color(fill_style.find('Color'))
        fill_data['blink'] = parse_blink(fill_style)

    line_data = {'forced': is_forced_line(line_style)}
    if line_data['forced']:
        line_data['pattern'] = line_style.get('Pattern', 'Solid')
        line_data['weight']  = float(line_style.get('Weight', '1'))
        line_data['color']   = parse_color(line_style.find('Color'))
        line_data['blink']   = parse_blink(line_style)

    outline_data = {'forced': False}
    if outline is not None and outline.get('Enabled') == 'true':
        outline_data['forced'] = True
        line = outline.find('Line')
        if line is not None:
            outline_data['pattern'] = line.get('Pattern', 'Solid')
            outline_data['weight']  = float(line.get('Weight', '1'))
            outline_data['color']   = parse_color(line.find('Color'))
        outline_data['blink'] = parse_blink(outline)

    return {
        'id': es_id, 'name': name,
        'category': cat, 'subgroup': subgroup,
        'usage': USAGE_DESCRIPTIONS.get(es_id, ''),
        'text': text_data, 'fill': fill_data,
        'line': line_data, 'outline': outline_data,
    }


def parse_xml(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    styles = []
    for es in root.findall('ES'):
        parsed = parse_es(es)
        if parsed:
            styles.append(parsed)
    cat_order = {'HMI': 0, 'Alarm': 1, 'UserDefined': 2}
    styles.sort(key=lambda s: (cat_order.get(s['category'], 99), s['id']))
    return styles


# ──────────────────────────────────────────────────────────────────────────────
# OUTPUT
# ──────────────────────────────────────────────────────────────────────────────

def generate_data(xml_path, output_dir):
    import os
    styles = parse_xml(xml_path)
    print(f"Parsed {len(styles)} styles:")
    print(f"  HMI:         {len([s for s in styles if s['category'] == 'HMI'])}")
    print(f"  Alarm:       {len([s for s in styles if s['category'] == 'Alarm'])}")
    print(f"  UserDefined: {len([s for s in styles if s['category'] == 'UserDefined'])}")

    out_path = os.path.join(output_dir, 'styles_data.js')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('// Auto-generated by generate_viewer.py — do not edit manually\n')
        f.write(f'const STYLES = {json.dumps(styles, ensure_ascii=False)};\n\n')
        f.write(f'const SAMPLE_TEXT_BY_NAME = {json.dumps(SAMPLE_TEXT_BY_NAME, ensure_ascii=False)};\n')
    print(f"\nGenerated: {out_path}")


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    generate_data(sys.argv[1], sys.argv[2])


if __name__ == '__main__':
    main()
