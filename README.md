# CESAN SCADA — Standard Style

Sistema de estilos HMI para AVEVA System Platform — Proyecto CESAN (Acciona).

**[→ Ver visor de estilos](https://jlanzaslopez.github.io/scada-styles/)**

---

## Archivos

| Archivo | Descripción |
|---|---|
| `Standard_Style.xml` | XML del sistema de estilos — importar en System Platform |
| `generate_viewer.py` | Script Python para regenerar el visor HTML |
| `docs/index.html` | Visor HTML (generado automáticamente por CI) |
| `CLAUDE_DESIGN_REFERENCE.md` | Referencia de diseño para Claude |

---

## Actualizar estilos

1. Edita `Standard_Style.xml` directamente en GitHub o sube una versión nueva
2. El workflow de GitHub Actions regenera `docs/index.html` automáticamente
3. GitHub Pages publica el visor actualizado en ~1 minuto

## Regenerar el visor localmente

```bash
python generate_viewer.py Standard_Style.xml docs/index.html
```

## Importar en System Platform

Importar `Standard_Style.xml` desde el IDE de AVEVA System Platform → Galaxy → Import Style Library.
