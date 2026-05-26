#!/usr/bin/env python3
"""
generate_viewer.py — Standalone style viewer generator for AVEVA System Platform
                     Standard_Style XML files.

Usage:
    python generate_viewer.py <input.xml> <output.html>
    python generate_viewer.py Standard_Style.xml viewer.html

Reads an ElementStyles XML file from System Platform and generates a self-contained
HTML viewer that displays all the styles grouped by category and subgroup, with
visual previews of each style's forced primitives (Text/Fill/Line/Outline).

To customize:
    - CATEGORIES: maps each ES Id to (category, subgroup). Edit to recategorize.
    - USAGE_DESCRIPTIONS: maps each ES Id to a short "real usage" string shown
      under the style name. Add/edit entries when you redefine the meaning of
      a style for your project.
    - SAMPLE_TEXT_BY_NAME (in HTML template): sample text shown in the preview
      for each style.

No external dependencies — pure Python 3 stdlib.
"""

import sys
import json
import xml.etree.ElementTree as ET


# ──────────────────────────────────────────────────────────────────────────────
# CATEGORY MAPPING
# Maps each ES Id to (category, subgroup). Edit to reorganize the viewer.
# Categories: 'HMI', 'Alarm', 'UserDefined'
# ──────────────────────────────────────────────────────────────────────────────
CATEGORIES = {
    # ─── HMI Element ───
    # Texto base
    10: ('HMI', 'Texto base'),
    20: ('HMI', 'Texto base'),
    30: ('HMI', 'Texto base'),
    35: ('HMI', 'Texto base'),
    40: ('HMI', 'Texto base'),
    50: ('HMI', 'Texto base'),
    60: ('HMI', 'Texto base'),
    # Estados de equipo
    70:  ('HMI', 'Estados de equipo'),
    77:  ('HMI', 'Estados de equipo'),
    80:  ('HMI', 'Estados de equipo'),
    83:  ('HMI', 'Estados de equipo'),
    85:  ('HMI', 'Estados de equipo'),
    90:  ('HMI', 'Estados de equipo'),
    100: ('HMI', 'Estados de equipo'),
    # Valores de proceso
    110: ('HMI', 'Valores de proceso'),
    120: ('HMI', 'Valores de proceso'),
    130: ('HMI', 'Valores de proceso'),
    140: ('HMI', 'Valores de proceso'),
    150: ('HMI', 'Valores de proceso'),
    160: ('HMI', 'Valores de proceso'),
    165: ('HMI', 'Valores de proceso'),
    270: ('HMI', 'Valores de proceso'),  # Tracker re-classified here
    # Líneas de proceso
    170: ('HMI', 'Líneas de proceso'),
    180: ('HMI', 'Líneas de proceso'),
    190: ('HMI', 'Líneas de proceso'),
    # Modos de control
    200: ('HMI', 'Modos de control'),
    210: ('HMI', 'Modos de control'),
    215: ('HMI', 'Modos de control'),
    # Vallado / contenedores
    220: ('HMI', 'Vallado/contenedores'),
    230: ('HMI', 'Vallado/contenedores'),
    # Límites de desviación
    250: ('HMI', 'Límites de desviación'),
    260: ('HMI', 'Límites de desviación'),
    # Sistema de seguridad
    263: ('HMI', 'Sistema de seguridad'),
    # Medidores y trackers
    265:  ('HMI', 'Medidores y trackers'),
    275:  ('HMI', 'Medidores y trackers'),
    1040: ('HMI', 'Medidores y trackers'),
    # Direcciones y navegación
    277: ('HMI', 'Direcciones y navegación'),
    278: ('HMI', 'Direcciones y navegación'),
    # Calidad
    480: ('HMI', 'Calidad'),
    484: ('HMI', 'Calidad'),
    488: ('HMI', 'Calidad'),
    # Intensidades de gris
    501: ('HMI', 'Intensidades de gris'),
    502: ('HMI', 'Intensidades de gris'),
    503: ('HMI', 'Intensidades de gris'),
    504: ('HMI', 'Intensidades de gris'),
    505: ('HMI', 'Intensidades de gris'),
    506: ('HMI', 'Intensidades de gris'),
    # Defaults del sistema
    570: ('HMI', 'Defaults del sistema'),
    580: ('HMI', 'Defaults del sistema'),
    590: ('HMI', 'Defaults del sistema'),
    600: ('HMI', 'Defaults del sistema'),
    610: ('HMI', 'Defaults del sistema'),
    620: ('HMI', 'Defaults del sistema'),
    630: ('HMI', 'Defaults del sistema'),
    640: ('HMI', 'Defaults del sistema'),

    # ─── Alarm Element ───
    # Fondo UNACK
    280: ('Alarm', 'Fondo UNACK'),
    290: ('Alarm', 'Fondo UNACK'),
    300: ('Alarm', 'Fondo UNACK'),
    310: ('Alarm', 'Fondo UNACK'),
    # Fondo ACK
    320: ('Alarm', 'Fondo ACK'),
    330: ('Alarm', 'Fondo ACK'),
    340: ('Alarm', 'Fondo ACK'),
    350: ('Alarm', 'Fondo ACK'),
    # Fondo RTN
    360: ('Alarm', 'Fondo RTN'),
    370: ('Alarm', 'Fondo RTN'),
    380: ('Alarm', 'Fondo RTN'),
    390: ('Alarm', 'Fondo RTN'),
    # Estados especiales
    400: ('Alarm', 'Estados especiales'),
    410: ('Alarm', 'Estados especiales'),
    420: ('Alarm', 'Estados especiales'),
    # Borde UNACK
    1050: ('Alarm', 'Borde UNACK'),
    1060: ('Alarm', 'Borde UNACK'),
    1070: ('Alarm', 'Borde UNACK'),
    1080: ('Alarm', 'Borde UNACK'),
    # Borde ACK
    1090: ('Alarm', 'Borde ACK'),
    1100: ('Alarm', 'Borde ACK'),
    1110: ('Alarm', 'Borde ACK'),
    1120: ('Alarm', 'Borde ACK'),
    # Borde RTN
    1130: ('Alarm', 'Borde RTN'),
    1140: ('Alarm', 'Borde RTN'),
    1150: ('Alarm', 'Borde RTN'),
    1160: ('Alarm', 'Borde RTN'),
    # Borde estados
    1170: ('Alarm', 'Borde estados'),
    1180: ('Alarm', 'Borde estados'),
    1190: ('Alarm', 'Borde estados'),
    1200: ('Alarm', 'Borde estados'),
}

# Add User_Defined slots automatically (24 total: Ids 800, 810, ..., 1030)
for es_id in range(800, 1031, 10):
    CATEGORIES[es_id] = ('UserDefined', 'Disponibles')


# ──────────────────────────────────────────────────────────────────────────────
# USAGE DESCRIPTIONS
# Short text shown under the style name explaining its real use in the project.
# Edit when you redefine a style's purpose.
# ──────────────────────────────────────────────────────────────────────────────
USAGE_DESCRIPTIONS = {
    # Valores de proceso (en uso)
    110: 'Valor mediano (default KPIs)',
    130: 'Valor mediano regular (secundario)',
    140: 'Valor pequeño (tablas, info densa)',
    270: 'Valor grande (KPIs destacados)',
    # Valores de proceso (en desuso)
    120: 'No aplica en agua/saneamiento',
    150: 'No aplica en agua/saneamiento',
    160: 'No aplica en agua/saneamiento',
    165: 'No aplica en agua/saneamiento',
    # Texto base
    10: 'Título de pantalla',
    20: 'Subtítulo de sección',
    30: 'Etiqueta general',
    35: 'Texto descriptivo pequeño',
    40: 'Nombre de tag/instrumento',
    50: 'Unidades de ingeniería',
    60: 'Color de fondo de pantalla',
    # Modos de control
    200: 'Modo automático',
    210: 'Modo manual',
    215: 'Modo cascada',
    # Vallado
    220: 'Tarjeta blanca con línea gris',
    230: 'Tarjeta de contraste',
    # Sistema de seguridad
    263: 'Banner de seguridad crítica',
    # Calidad
    480: 'Calidad: buena',
    484: 'Calidad: aceptable',
    488: 'Calidad: mala',
    # Navegación
    278: 'Botones de navegación',
}


# ──────────────────────────────────────────────────────────────────────────────
# SAMPLE TEXT FOR PREVIEWS
# What text/value to render in the preview area for each style.
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
# XML PARSING
# ──────────────────────────────────────────────────────────────────────────────
def parse_color(color_elem):
    """Parse a <Color> element and return a dict with type/css/components."""
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
        return {
            'type': 'solid',
            'r': r, 'g': g, 'b': b, 'a': a,
            'transparency': trans,
            'css': css,
        }
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
    """Parse a Blink child element if present."""
    blink = parent.find('Blink')
    if blink is None:
        return None
    return {
        'speed': blink.get('Speed', 'Slow'),
        'color': parse_color(blink.find('Color')),
    }


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
    """Parse a single <ES> element into a dict, or return None if not categorized."""
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
    outline = es.find('Outline')

    # Text
    text_data = {'forced': is_forced_text(text_style)}
    if text_data['forced']:
        font = text_style.find('Font')
        if font is not None:
            text_data['font'] = font.get('Name')
            text_data['size'] = float(font.get('Size'))
            text_data['bold'] = font.get('Bold') == 'true'
            text_data['italic'] = font.get('Italic') == 'true'
        color = text_style.find('Color')
        if color is not None:
            text_data['color'] = parse_color(color)
        text_data['blink'] = parse_blink(text_style)

    # Fill
    fill_data = {'forced': is_forced_fill(fill_style)}
    if fill_data['forced']:
        fill_data['color'] = parse_color(fill_style.find('Color'))
        fill_data['blink'] = parse_blink(fill_style)

    # Line
    line_data = {'forced': is_forced_line(line_style)}
    if line_data['forced']:
        line_data['pattern'] = line_style.get('Pattern', 'Solid')
        line_data['weight'] = float(line_style.get('Weight', '1'))
        line_data['color'] = parse_color(line_style.find('Color'))
        line_data['blink'] = parse_blink(line_style)

    # Outline
    outline_data = {'forced': False}
    if outline is not None and outline.get('Enabled') == 'true':
        outline_data['forced'] = True
        line = outline.find('Line')
        if line is not None:
            outline_data['pattern'] = line.get('Pattern', 'Solid')
            outline_data['weight'] = float(line.get('Weight', '1'))
            outline_data['color'] = parse_color(line.find('Color'))
        outline_data['blink'] = parse_blink(outline)

    return {
        'id': es_id,
        'name': name,
        'category': cat,
        'subgroup': subgroup,
        'usage': USAGE_DESCRIPTIONS.get(es_id, ''),
        'text': text_data,
        'fill': fill_data,
        'line': line_data,
        'outline': outline_data,
    }


def parse_xml(xml_path):
    """Parse the entire XML file and return a sorted list of style dicts."""
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
# HTML TEMPLATE
# ──────────────────────────────────────────────────────────────────────────────
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Visor de Estilos · Standard_Style</title>
<style>
  :root {
    --bg: #f4f6f8;
    --card-bg: #ffffff;
    --border: #d8dde4;
    --border-strong: #b0b8c4;
    --text-primary: #1a2332;
    --text-secondary: #5a6577;
    --text-muted: #8c95a4;
    --accent: #0a6ebd;
    --header-bg: #ffffff;
    --preview-bg: #fafbfc;
  }
  body.dark {
    --bg: #0c1015;
    --card-bg: #181f28;
    --border: #2a3340;
    --border-strong: #3d4754;
    --text-primary: #e2e8f0;
    --text-secondary: #8899aa;
    --text-muted: #5c6b7d;
    --accent: #3b9ae0;
    --header-bg: #141a21;
    --preview-bg: #0f141a;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'Segoe UI', system-ui, sans-serif;
    background: var(--bg);
    color: var(--text-primary);
    transition: background 0.2s, color 0.2s;
  }
  header {
    position: sticky; top: 0;
    background: var(--header-bg);
    border-bottom: 1px solid var(--border);
    padding: 14px 24px;
    display: flex; align-items: center; gap: 16px; flex-wrap: wrap;
    z-index: 10;
  }
  h1 { font-size: 16px; font-weight: 700; }
  h1 small { font-weight: 400; color: var(--text-muted); margin-left: 8px; font-size: 12px; }
  .filters { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
  .filter-btn {
    background: transparent; border: 1px solid var(--border);
    color: var(--text-secondary); padding: 5px 12px; border-radius: 4px;
    font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em;
    cursor: pointer; font-family: inherit; transition: all 0.15s;
  }
  .filter-btn:hover { color: var(--text-primary); border-color: var(--border-strong); }
  .filter-btn.active { background: var(--accent); color: #fff; border-color: var(--accent); }
  .toggle-theme {
    margin-left: auto; background: transparent; border: 1px solid var(--border);
    color: var(--text-secondary); padding: 6px 14px; border-radius: 4px;
    cursor: pointer; font-family: inherit; font-size: 11px; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.04em;
  }
  .toggle-theme:hover { color: var(--text-primary); }
  .legend {
    display: flex; gap: 12px; font-size: 10px; color: var(--text-muted);
    align-items: center; padding: 8px 24px;
    border-bottom: 1px solid var(--border); background: var(--header-bg); flex-wrap: wrap;
  }
  .legend-item { display: flex; align-items: center; gap: 4px; }
  .pill {
    display: inline-flex; align-items: center; justify-content: center;
    width: 18px; height: 18px; border-radius: 3px;
    font-size: 9px; font-weight: 700;
    background: var(--border); color: var(--text-secondary);
  }
  .pill.on { background: var(--accent); color: #fff; }
  .pill.blink-on { background: #f59e0b; color: #fff; }
  main { padding: 16px 24px 60px; }
  .subgroup { margin-bottom: 24px; }
  .subgroup-title {
    font-size: 11px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.08em; color: var(--text-muted);
    margin-bottom: 8px; padding-bottom: 4px;
    border-bottom: 1px solid var(--border);
  }
  .subgroup-title .cat-tag {
    display: inline-block; background: var(--accent); color: #fff;
    padding: 1px 6px; border-radius: 2px; font-size: 9px;
    margin-right: 8px; letter-spacing: 0.05em;
  }
  .subgroup-title .cat-tag.alarm { background: #dc2626; }
  .subgroup-title .cat-tag.userdefined { background: #16a34a; }
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 10px;
  }
  .card {
    background: var(--card-bg); border: 1px solid var(--border);
    border-radius: 6px; padding: 10px 12px;
    display: flex; flex-direction: column; gap: 8px;
    min-height: 165px;
  }
  .card.unused { border-color: #f0abfc; border-style: dashed; }
  .card-header {
    display: flex; justify-content: space-between;
    align-items: flex-start; gap: 6px;
  }
  .card-name {
    font-size: 11px; font-weight: 600;
    color: var(--text-primary); line-height: 1.3; word-break: break-word;
  }
  .card-usage {
    font-size: 10px; font-weight: 400;
    color: var(--text-secondary); line-height: 1.3;
    margin-top: 2px; font-style: italic;
  }
  .card-name .unused-tag {
    display: inline-block; background: #ec4899; color: #fff;
    padding: 1px 5px; border-radius: 2px; font-size: 8px;
    margin-left: 4px; text-transform: uppercase;
    letter-spacing: 0.05em; vertical-align: middle;
  }
  .card-id {
    font-size: 10px; color: var(--text-muted);
    font-family: 'Consolas', monospace; flex-shrink: 0;
  }
  .pills { display: flex; gap: 3px; }
  .preview {
    flex: 1; background: var(--preview-bg);
    border: 1px dashed var(--border); border-radius: 4px;
    display: flex; align-items: center; justify-content: center;
    padding: 12px 8px; min-height: 60px;
    position: relative; overflow: hidden;
  }
  .preview-text { line-height: 1.2; }
  .meta {
    font-size: 9px; color: var(--text-muted);
    font-family: 'Consolas', monospace; line-height: 1.4;
  }
  .meta-label {
    color: var(--text-muted); font-weight: 600;
    text-transform: uppercase; font-size: 8px;
    letter-spacing: 0.05em; min-width: 28px;
  }

  .empty-msg { color: var(--text-muted); font-size: 10px; font-style: italic; }
  .meta-row { display: flex; gap: 4px; align-items: center; }
  .meta-val { flex: 1; }
  .meta-right { display: flex; align-items: center; justify-content: flex-end; gap: 4px; }
  .color-hex {
    font-family: 'Consolas', monospace; font-size: 9px;
    color: var(--text-secondary); cursor: pointer; letter-spacing: 0.03em;
    transition: color 0.1s;
  }
  .color-hex:hover { color: var(--accent); }
  .available-msg {
    color: #16a34a; font-size: 11px; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.05em;
  }
</style>
</head>
<body>

<header>
  <h1>Visor de Estilos <small>Standard_Style · __TOTAL__ estilos</small></h1>
  <div class="filters">
    <button class="filter-btn active" data-cat="all">Todas</button>
    <button class="filter-btn" data-cat="HMI">HMI Element</button>
    <button class="filter-btn" data-cat="Alarm">Alarm Element</button>
    <button class="filter-btn" data-cat="UserDefined">User Defined</button>
  </div>
  <div class="filters">
    <button class="filter-btn active" data-force="all">Cualquier primitiva</button>
    <button class="filter-btn" data-force="text">Solo con texto</button>
    <button class="filter-btn" data-force="fill">Solo con fondo</button>
    <button class="filter-btn" data-force="line">Solo con línea</button>
    <button class="filter-btn" data-force="outline">Solo con outline</button>
  </div>
  <button class="toggle-theme" onclick="document.body.classList.toggle('dark')">🌓 Tema</button>
  <button class="toggle-theme" onclick="downloadXML()">⬇ Descargar XML</button>
</header>

<div class="legend">
  <span class="legend-item"><span class="pill on">T</span> Texto forzado</span>
  <span class="legend-item"><span class="pill on">F</span> Fondo (Fill) forzado</span>
  <span class="legend-item"><span class="pill on">L</span> Línea forzada</span>
  <span class="legend-item"><span class="pill on">O</span> Outline forzado</span>
  <span class="legend-item"><span class="pill on">B</span> Blink activo</span>
  <span class="legend-item">·</span>
  <span class="legend-item">Pill apagada = libre, configurable en cada componente</span>
  <span class="legend-item">·</span>
  <span class="legend-item" style="color:#ec4899; font-weight:600;">Magenta = en desuso</span>
</div>

<main id="main"></main>

<script>
const STYLES = __STYLES_JSON__;

const SAMPLE_TEXT_BY_NAME = __SAMPLE_TEXT_JSON__;

function isUnused(s) {
  if (s.fill && s.fill.forced && s.fill.color && s.fill.color.type === 'solid') {
    return s.fill.color.r === 255 && s.fill.color.g === 0 && s.fill.color.b === 255;
  }
  return false;
}

function getSampleText(name) {
  if (SAMPLE_TEXT_BY_NAME[name] !== undefined) return SAMPLE_TEXT_BY_NAME[name];
  if (name.startsWith('Intensity')) return 'Texto';
  if (name.startsWith('User_Defined_')) return '';
  if (name.startsWith('Alarm_')) return name.replace('Alarm_', '').replace(/_/g, ' ');
  return name.replace(/_/g, ' ');
}

function pill(letter, on) {
  const cls = on ? (letter === 'B' ? 'blink-on' : 'on') : '';
  return '<span class="pill ' + cls + '">' + letter + '</span>';
}

function colorToCSS(c) {
  if (!c) return 'transparent';
  if (c.type === 'pattern') {
    return 'repeating-linear-gradient(45deg, ' + c.fore + ' 0 2px, ' + c.back + ' 2px 6px)';
  }
  return c.css;
}

function renderPreview(s, unused) {
  const hasText = s.text.forced;
  const hasFill = s.fill.forced;
  const hasLine = s.line.forced;
  const hasOutline = s.outline.forced;
  const isAvailable = s.category === 'UserDefined' && !hasText && !hasFill && !hasLine && !hasOutline;

  const animId = 'bk' + s.id;
  let extraStyle = '';

  // Fill blink: animate background-color between c1 and c2
  let bgStyle = '';
  if (hasFill && s.fill.color) {
    const c1 = s.fill.color.type === 'pattern' ? colorToCSS(s.fill.color) : s.fill.color.css;
    if (s.fill.blink && s.fill.blink.color) {
      const c2 = s.fill.blink.color.css;
      extraStyle += '@keyframes ' + animId + 'f{0%,49%{background:' + c1 + '}50%,100%{background:' + c2 + '}} ';
      bgStyle = 'background:' + c1 + ';animation:' + animId + 'f 1.4s step-end infinite;';
    } else {
      bgStyle = 'background:' + c1 + ';';
    }
  }

  // Line/Outline blink: animate border-color between c1 and c2
  let borderStyle = '';
  let borderBase = '';
  let borderBlink2 = '';
  let borderWeight = 1;
  if (hasOutline && s.outline.color) {
    borderWeight = s.outline.weight || 1;
    borderBase = colorToCSS(s.outline.color);
    if (s.outline.blink && s.outline.blink.color) borderBlink2 = s.outline.blink.color.css;
  } else if (hasLine && s.line.color) {
    borderWeight = s.line.weight || 1;
    borderBase = s.line.color.type === 'pattern' ? s.line.color.fore : s.line.color.css;
    if (s.line.blink && s.line.blink.color) borderBlink2 = s.line.blink.color.css;
  }
  if (borderBase) {
    if (borderBlink2) {
      extraStyle += '@keyframes ' + animId + 'b{0%,49%{border-color:' + borderBase + '}50%,100%{border-color:' + borderBlink2 + '}} ';
      borderStyle = 'border:' + borderWeight + 'px solid ' + borderBase + ';animation:' + animId + 'b 1.4s step-end infinite;';
      if (bgStyle.includes('animation:')) {
        // Merge both animations
        bgStyle = bgStyle.replace('animation:', 'animation:' + animId + 'b 1.4s step-end infinite,');
        borderStyle = 'border:' + borderWeight + 'px solid ' + borderBase + ';';
      }
    } else {
      borderStyle = 'border:' + borderWeight + 'px solid ' + borderBase + ';';
    }
  }

  const styleTag = extraStyle ? '<style>' + extraStyle + '</style>' : '';

  let textHTML = '';
  if (unused) {
    textHTML = '<span class="preview-text" style="color:#fff;font-weight:700;font-size:11px;text-transform:uppercase;letter-spacing:0.05em;">EN DESUSO</span>';
  } else if (isAvailable) {
    textHTML = '<span class="available-msg">Disponible</span>';
  } else if (hasText) {
    const t = s.text;
    const fontFamily = t.font ? "'" + t.font + "', sans-serif" : 'inherit';
    const size = t.size ? t.size + 'pt' : 'inherit';
    const weight = t.bold ? '700' : '400';
    const italic = t.italic ? 'italic' : 'normal';
    const color = (t.color && t.color.css) ? t.color.css : 'currentColor';
    const sample = getSampleText(s.name);
    if (sample === '') {
      textHTML = '<span class="empty-msg">(sin muestra)</span>';
    } else {
      textHTML = '<span class="preview-text" style="font-family:' + fontFamily + ';font-size:' + size + ';font-weight:' + weight + ';font-style:' + italic + ';color:' + color + ';">' + sample + '</span>';
    }
  } else {
    textHTML = '<span class="empty-msg">—</span>';
  }

  return styleTag + '<div class="preview" style="' + bgStyle + ' ' + borderStyle + '">' + textHTML + '</div>';
}
function toHex(color) {
  if (!color || color.type !== 'solid') return '';
  const h = v => v.toString(16).padStart(2,'0').toUpperCase();
  return '#' + h(color.r) + h(color.g) + h(color.b);
}

function colorLine(color) {
  if (!color || color.type !== 'solid') return '';
  return color.css + ' <span class="color-hex" onclick="copyHex(this)" title="Copiar hex">' + toHex(color) + '</span>';
}

function copyHex(el) {
  navigator.clipboard.writeText(el.textContent).then(() => {
    const orig = el.textContent;
    el.textContent = '✓';
    setTimeout(() => el.textContent = orig, 900);
  });
}

function renderMeta(s) {
  const lines = [];
  if (s.text.forced && s.text.font) {
    lines.push('<div class="meta-row"><span class="meta-label">FONT</span><span class="meta-val">' + s.text.font + ' ' + s.text.size + 'pt' + (s.text.bold ? ' bold' : '') + '</span></div>');
  }
  if (s.text.forced && s.text.color) {
    lines.push('<div class="meta-row"><span class="meta-label">COL</span><span class="meta-val meta-right">' + colorLine(s.text.color) + '</span></div>');
  }
  if (s.fill.forced && s.fill.color) {
    if (s.fill.color.type === 'pattern') {
      lines.push('<div class="meta-row"><span class="meta-label">FILL</span><span class="meta-val">pattern ' + s.fill.color.hatch + '</span></div>');
    } else {
      lines.push('<div class="meta-row"><span class="meta-label">FILL</span><span class="meta-val meta-right">' + colorLine(s.fill.color) + '</span></div>');
      if (s.fill.blink && s.fill.blink.color) {
        lines.push('<div class="meta-row"><span class="meta-label">↔</span><span class="meta-val meta-right">' + colorLine(s.fill.blink.color) + '</span></div>');
      }
    }
  }
  if (s.line.forced) {
    const chip = s.line.color && s.line.color.type === 'solid' ? colorLine(s.line.color) : (s.line.color ? 'pattern' : '');
    lines.push('<div class="meta-row"><span class="meta-label">LINE</span><span class="meta-val meta-right">' + s.line.weight + 'px ' + chip + '</span></div>');
    if (s.line.blink && s.line.blink.color) {
      lines.push('<div class="meta-row"><span class="meta-label">↔</span><span class="meta-val meta-right">' + colorLine(s.line.blink.color) + '</span></div>');
    }
  }
  if (s.outline.forced) {
    const chip = s.outline.color && s.outline.color.type === 'solid' ? colorLine(s.outline.color) : '';
    lines.push('<div class="meta-row"><span class="meta-label">OUT</span><span class="meta-val meta-right">' + s.outline.weight + 'px ' + chip + '</span></div>');
  }
  return '<div class="meta">' + lines.join('') + '</div>';
}


function renderCard(s) {
  const unused = isUnused(s);
  const unusedClass = unused ? ' unused' : '';
  const unusedTag = unused ? ' <span class="unused-tag">desuso</span>' : '';
  const usageHTML = s.usage ? '<div class="card-usage">' + s.usage + '</div>' : '';
  const blinkActive = (s.text.forced && s.text.blink) || (s.fill.forced && s.fill.blink) || (s.line.forced && s.line.blink) || (s.outline.forced && s.outline.blink);
  const pills = '<div class="pills">' +
    pill('T', s.text.forced) +
    pill('F', s.fill.forced) +
    pill('L', s.line.forced) +
    pill('O', s.outline.forced) +
    pill('B', blinkActive) +
    '</div>';
  return '<div class="card' + unusedClass + '" data-cat="' + s.category + '" data-text="' + s.text.forced + '" data-fill="' + s.fill.forced + '" data-line="' + s.line.forced + '" data-outline="' + s.outline.forced + '">' +
    '<div class="card-header">' +
      '<div>' +
        '<div class="card-name">' + s.name + unusedTag + '</div>' +
        usageHTML +
      '</div>' +
      '<div class="card-id">#' + s.id + '</div>' +
    '</div>' +
    pills +
    renderPreview(s, unused) +
    renderMeta(s) +
  '</div>';
}

function render() {
  const main = document.getElementById('main');
  const groups = {};
  STYLES.forEach(s => {
    const key = s.category + '|' + s.subgroup;
    if (!groups[key]) groups[key] = [];
    groups[key].push(s);
  });
  const catOrder = { HMI: 0, Alarm: 1, UserDefined: 2 };
  const sortedKeys = Object.keys(groups).sort((a, b) => {
    const catA = a.split('|')[0];
    const catB = b.split('|')[0];
    if (catOrder[catA] !== catOrder[catB]) return catOrder[catA] - catOrder[catB];
    return a.localeCompare(b);
  });
  let html = '';
  sortedKeys.forEach(key => {
    const parts = key.split('|');
    const cat = parts[0];
    const subgroup = parts[1];
    let tagClass = 'cat-tag';
    let tagText = cat;
    if (cat === 'Alarm') { tagClass += ' alarm'; tagText = 'ALM'; }
    else if (cat === 'UserDefined') { tagClass += ' userdefined'; tagText = 'USR'; }
    else { tagText = 'HMI'; }
    html += '<div class="subgroup" data-cat="' + cat + '">' +
      '<div class="subgroup-title"><span class="' + tagClass + '">' + tagText + '</span>' + subgroup + '</div>' +
      '<div class="grid">' +
        groups[key].map(renderCard).join('') +
      '</div>' +
    '</div>';
  });
  main.innerHTML = html;
  applyFilters();
}

let filterCat = 'all';
let filterForce = 'all';

function applyFilters() {
  document.querySelectorAll('.subgroup').forEach(sg => {
    const cards = sg.querySelectorAll('.card');
    let visible = 0;
    cards.forEach(card => {
      const catMatch = filterCat === 'all' || card.dataset.cat === filterCat;
      let forceMatch = true;
      if (filterForce !== 'all') {
        forceMatch = card.dataset[filterForce] === 'true';
      }
      const show = catMatch && forceMatch;
      card.style.display = show ? '' : 'none';
      if (show) visible++;
    });
    sg.style.display = visible > 0 ? '' : 'none';
  });
}

document.querySelectorAll('[data-cat]').forEach(btn => {
  if (btn.tagName === 'BUTTON') {
    btn.addEventListener('click', () => {
      document.querySelectorAll('[data-cat]').forEach(b => {
        if (b.tagName === 'BUTTON') b.classList.remove('active');
      });
      btn.classList.add('active');
      filterCat = btn.dataset.cat;
      applyFilters();
    });
  }
});
document.querySelectorAll('[data-force]').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('[data-force]').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    filterForce = btn.dataset.force;
    applyFilters();
  });
});

function downloadXML() {
  const a = document.createElement('a');
  a.href = 'Standard_Style.xml';
  a.download = 'Standard_Style.xml';
  a.click();
}

render();
</script>
</body>
</html>
'''


def generate_viewer(xml_path, output_path):
    """Parse the XML and write the HTML viewer."""
    styles = parse_xml(xml_path)
    print(f"Parsed {len(styles)} styles:")
    print(f"  HMI:         {len([s for s in styles if s['category'] == 'HMI'])}")
    print(f"  Alarm:       {len([s for s in styles if s['category'] == 'Alarm'])}")
    print(f"  UserDefined: {len([s for s in styles if s['category'] == 'UserDefined'])}")

    styles_json = json.dumps(styles, ensure_ascii=False)
    sample_json = json.dumps(SAMPLE_TEXT_BY_NAME, ensure_ascii=False)

    html = HTML_TEMPLATE \
        .replace('__TOTAL__', str(len(styles))) \
        .replace('__STYLES_JSON__', styles_json) \
        .replace('__SAMPLE_TEXT_JSON__', sample_json)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"\nGenerated viewer: {output_path}")


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    xml_path = sys.argv[1]
    output_path = sys.argv[2]
    generate_viewer(xml_path, output_path)


if __name__ == '__main__':
    main()
