# EcoImpacto

Aplicación web (un solo archivo, sin dependencias) para:

1. Registrar las **actividades** de un proyecto por etapa (construcción, operación, mantenimiento, cierre).
2. Identificar **aspectos ambientales** y sus **impactos** sobre **agua, aire y suelo**.
3. **Evaluar** cada impacto y obtener una matriz actividad × componente, un resumen y un registro exportable.

## Metodología de evaluación (simplificada)

Cada impacto se califica de 1 a 5 en intensidad, extensión, duración, persistencia/reversibilidad y probabilidad:

```
Significancia = (3×Intensidad + 2×Extensión + Duración + Persistencia) × Probabilidad ÷ 5
```

| Valor | Nivel |
|---|---|
| < 10 | Bajo |
| 10 – 19 | Moderado |
| 20 – 27 | Severo |
| ≥ 28 | Crítico |

Los impactos positivos se registran aparte, sin puntaje de severidad. Ajusta la fórmula y los umbrales (`score()` y `level()` en `index.html`) a la metodología que exija tu autoridad ambiental (por ejemplo Conesa o Leopold).

## Uso

- Abre `index.html` en el navegador, o publícalo con **GitHub Pages**.
- Los datos se guardan en el navegador (`localStorage`). Usa **Guardar JSON** / **Cargar JSON** para respaldar o compartir, y **Exportar CSV** para Excel.

## Publicar en GitHub Pages

1. Crea un repositorio nuevo en GitHub y sube `index.html` y `README.md`.
2. Ve a **Settings → Pages**, elige la rama `main` y la carpeta `/ (root)`.
3. Tu app quedará en `https://<tu-usuario>.github.io/<repositorio>/`.
