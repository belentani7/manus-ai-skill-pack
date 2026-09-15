# open-data

Pack de datos abiertos de **modelos LLM (OpenRouter)**.

- **Fuente:** <https://openrouter.ai/api/v1/models>
- **Clave de API:** no requiere.
- **Generado:** ver `meta.generated_at` en `ai-models.json`.

## Ficheros

| Fichero | Descripcion |
|---|---|
| `ai-models.json` | Registros con metadatos + bloque `meta` |
| `ai-models.csv` | El mismo pack en tabla |

## Regenerar

```bash
python scripts/fetch_open_data.py
```

Usa solo la libreria estandar.

## Licencia

Datos de OpenRouter; revisa sus terminos. Codigo del pack: MIT.
