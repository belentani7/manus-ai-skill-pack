# manus-ai-skill-pack

Paquete de skills de IA.

## Qué es

Una colección de skills reutilizables: instrucciones empaquetadas que un agente carga para
resolver tareas concretas. La idea es escribir la habilidad una vez y usarla muchas.

## Estructura

- Cada skill es un directorio con su `SKILL.md` (cuándo se activa y qué hace). El paquete
  incluye ~290 skills (287 archivos `SKILL.md`), agrupadas por origen en el prefijo del
  directorio: `abcnuts-`, `agency-`, `anthropics-`, `bmcp-`, `openai-`, `taste-`,
  `greensock-`, `firecrawl-`, entre otros.
- [`MASTER-AGENT.md`](MASTER-AGENT.md) — prompt maestro agnóstico de proyecto que descubre
  el repo y selecciona arquitectura y skills.
- [`index.html`](index.html) y [`ecosistema.html`](ecosistema.html) — catálogo navegable
  del paquete.
- [`docs/`](docs/) — página publicada en GitHub Pages (workflow
  `.github/workflows/deploy-pages.yml`, que sube `docs/` con `upload-pages-artifact`).
- [`magic/`](magic/) y [`open-data/`](open-data/) — material auxiliar con sus propios
  README.

## Estado

Empaquetado. El contenido es la parte viva: crece con cada habilidad nueva.

## Licencia

MIT (ver [`LICENSE`](LICENSE)).
