# scripts

| Script | Qué hace |
|---|---|
| `fetch_open_data.py` | Regenera el pack de `open-data/` desde la fuente pública. |
| `find_skills.py` | Busca skills existentes por nombre, carpeta y descripción sin red ni dependencias. |

```bash
python scripts/find_skills.py video
python scripts/find_skills.py --json --limit 5
python scripts/fetch_open_data.py
```

El buscador examina únicamente carpetas de skills con `SKILL.md` en la raíz del pack, ordena resultados de forma determinista y devuelve código de salida 1 si no hay coincidencias.
