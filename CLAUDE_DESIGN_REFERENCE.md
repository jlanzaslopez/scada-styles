# CESAN SCADA — Design Reference for Claude

> Este fichero es la referencia canónica del sistema de estilos `Standard_Style.xml`.
> Úsalo como contexto en conversaciones nuevas junto con el XML actual.
> Última actualización: v6

---

## Proyecto

- **Cliente:** CESAN — agua y saneamiento, Espírito Santo, Brasil (proyecto Acciona)
- **Plataforma:** AVEVA System Platform con OMI
- **Pantallas objetivo:** operador 1920×1080 + videowall (dimensiones pendientes)
- **Tema:** claro (light), moderno y limpio

---

## Tipografía

| Uso | Fuente | Tamaño | Peso |
|---|---|---|---|
| Textos generales | `Segoe UI Variable Text Semilight` | variable | variable |
| Valores numéricos | `Consolas` | variable | variable |

**Regla clave:** Consolas es obligatoria para cualquier valor numérico porque el placeholder `#` de System Platform debe ocupar el mismo ancho que los dígitos reales en runtime. Las fuentes proporcionales causan saltos visuales.

### Jerarquía tipográfica activa

| ES ID | Nombre | Fuente | Tamaño | Peso | Uso |
|---|---|---|---|---|---|
| 10 | `Title` | Segoe UI Variable Text Semilight | 18pt | Bold | Títulos de pantalla |
| 20 | `Heading` | Segoe UI Variable Text Semilight | 14pt | Bold | Cabeceras de sección |
| 30 | `Label` | Segoe UI Variable Text Semilight | 10pt | Regular | Etiquetas genéricas |
| 35 | `Descriptor` | Segoe UI Variable Text Semilight | 8pt | Regular | Texto auxiliar, notas |
| 40 | `Tagname` | Segoe UI Variable Text Semilight | 10pt | Bold | Nombre de tags/equipos |
| 50 | `Engineering_Units` | Segoe UI Variable Text Semilight | 8pt | Regular | Unidades (m³/h, bar…) |
| 110 | `Actual_Value` | Consolas | 12pt | Bold | Valor mediano (KPIs) |
| 130 | `Setpoint` | Consolas | 12pt | Regular | Valor secundario/setpoint |
| 140 | `Recent_Value_Range` | Consolas | 10pt | Regular | Tablas, info densa |
| 270 | `Tracker` | Consolas | 18pt | Bold | KPI destacado / grande |

---

## Paleta de colores

### Alarmas

| Nivel | Color fuerte (texto/borde) | Color pastel (fondo) |
|---|---|---|
| Critical | `#C0392B` | `#FADADD` |
| High | `#E8650A` | `#FDDBB0` |
| Med | `#D4AC0D` | `#FDF4C0` |
| Low | `#1A5276` | `#D6EAF8` |

### Estados de equipo

| Estado | Fill | Hex |
|---|---|---|
| `Not_Running` | Gris claro (parado) | `#D9D8D8` |
| `Active` | Verde medio (en marcha) | `#5D9E6E` |
| `Transitioning` | Blink Not_Running ↔ Active | — |
| `Interlocked` | Gris oscuro (fuera de servicio) | `#9E9E9E` |

### Contenedores (Fencing)

| Estilo | Fondo | Borde |
|---|---|---|
| `Fencing_1` | `#FFFFFF` | 1px `#D8DDE4` |
| `Fencing_2` | `#F0F2F5` | 1px `#B0B8C4` |

### Líneas de proceso

| Estilo | Color | Uso |
|---|---|---|
| `Process_Line_Primary` | `#826501` | Tuberías esgoto (aguas residuales) |
| `Process_Line_Secondary` | `#5DADE2` | Agua limpia (ETE) |

### Defaults del sistema

| Estilo | Fill | Texto | Hex |
|---|---|---|---|
| `Default_Background` | Blanco | — | `#FFFFFF` |
| `Default_Foreground` | Gris suave | — | `#F0F2F5` |
| `Default_Accent` | Gris medio | 12pt bold mismo color | `#9E9E9E` |
| `Default_Selected` | Azul medio | 12pt bold mismo color | `#2E86C1` |
| `Default_Hover` | Azul oscuro | 12pt bold mismo color | `#1A5276` |
| `Default_FontFamily` | — | 12pt bold, sin color forzado | — |
| `Default_FontStyle` | — | 10pt regular, sin color forzado | — |

---

## Lógica de alarmas

### Alarm_XXX (para iconos y símbolos de equipo)

| Estado | TextStyle | FillStyle | LineStyle | Blink |
|---|---|---|---|---|
| UNACK | Color fuerte | Color fuerte | Ninguno | Fill: fuerte → pastel |
| ACK | Color fuerte | Color fuerte | Ninguno | No |
| RTN | — | Pastel | Ninguno | No |

### AlarmBorder_XXX (para contenedores tipo Fencing)

| Estado | FillStyle | LineStyle | Blink |
|---|---|---|---|
| UNACK | Pastel | 3px fuerte | Line: fuerte → pastel |
| ACK | Pastel | 3px fuerte | No |
| RTN | Pastel | 1px `#D8DDE4` | No |

**Estados especiales** (Inhibited, Supressed, Shelved, Silenced) → todos en desuso (`#FF00FF`).

---

## Reglas de diseño

### Primitivas forzadas vs libres

Cada `ElementStyle` tiene 4 primitivas: `TextStyle`, `FillStyle`, `LineStyle`, `Outline`.
- **Vacía** = no forzada → el componente la define libremente
- **Con contenido** = forzada → todos los componentes que usen el estilo la heredan

**Principio:** forzar solo lo necesario. Ejemplo: `Actual_Value` fuerza solo el texto (fuente, tamaño, color) y deja fondo y borde libres → el valor siempre se ve igual tipográficamente, pero el contenedor puede ser blanco, alarmado, etc.

### Outline vs LineStyle

- **`Outline`** = contorno externo del objeto en OMI. Nunca usarlo para estilos de alarma de borde — causa errores de importación en System Platform.
- **`LineStyle`** = borde interior del elemento gráfico. Usar siempre para `AlarmBorder_XXX`.

### Blink

- El blink en `FillStyle` alterna el fondo del elemento.
- El blink en `LineStyle` alterna el borde del elemento.
- Los UNACK siempre llevan blink. Los ACK y RTN nunca.

### Estilos en desuso

Fill `#FF00FF` (magenta chillón) — inconfundible visualmente, nunca se usa en producción.

---

## Estructura del XML

```
Standard_Style.xml
├── Categoría 1 — HMI Element (55 ES)
│   ├── Texto base: Title(10), Heading(20), Label(30), Descriptor(35), Tagname(40), Engineering_Units(50)
│   ├── Estados de equipo: Not_Running(77), Active(80), Transitioning(90), Interlocked(100)
│   ├── Valores de proceso: Actual_Value(110), Setpoint(130), Recent_Value_Range(140), Tracker(270)
│   ├── Líneas de proceso: Process_Line_Primary(180), Process_Line_Secondary(190)
│   ├── Contenedores: Fencing_1(220), Fencing_2(230)
│   ├── Calidad: Good(480), Satisfactory(484), Bad(488)
│   ├── Intensidades: Intensity1-6 (501-506)
│   └── Defaults: Default_Background(570)…Default_FocusIndicator(640)
├── Categoría 2 — Alarm Element (31 ES)
│   ├── Alarm_XXX_UNACK/ACK/RTN × Critical/High/Med/Low
│   ├── AlarmBorder_XXX_UNACK/ACK/RTN × Critical/High/Med/Low
│   └── Estados especiales → todos DESUSO
└── Categoría 3 — User Defined (24 huecos, todos vacíos)
    └── User_Defined_01…User_Defined_24 (IDs 800-1030)
```

---

## Workflow de iteración

1. Decidir cambios en conversación
2. Claude edita `Standard_Style.xml` en el repo (vía MCP GitHub) o genera script Python de patch
3. GitHub Actions detecta el push → ejecuta `generate_viewer.py` → publica `docs/index.html` en GitHub Pages
4. Validar en el visor web
5. Importar en System Platform para validación final

### Script de patch (patrón estándar)

```python
import re

def replace_es_block(xml, es_id, new_block):
    pattern = rf'(\s*<ES Id="{es_id}"[^>]*>.*?</ES>)'
    match = re.search(pattern, xml, re.DOTALL)
    if not match:
        return xml
    return xml[:match.start()] + "\n" + new_block + xml[match.end():]
```

---

## Pendiente / próximos pasos

- [ ] Definir dimensiones del videowall → crear variantes XL si hace falta (User_Defined)
- [ ] Revisar subgrupo Calidad (Good/Satisfactory/Bad) y Modos de control
- [ ] Decidir qué User_Defined activar (estados de iconos animados, variantes tipográficas)
- [ ] Validar `Segoe UI Variable Text Semilight` en System Platform (puede requerir nombre alternativo)
- [ ] Validar AlarmBorder LineStyle blink en OMI Web vs cliente nativo
