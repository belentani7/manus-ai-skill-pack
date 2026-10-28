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
- [`docs/`](docs/) — sitio preparado para GitHub Pages (workflow
  `.github/workflows/deploy-pages.yml`, que sube `docs/` con `upload-pages-artifact`; el despliegue actual no se ha verificado).
- [`magic/`](magic/) y [`open-data/`](open-data/) — material auxiliar con sus propios
  README.

## Estado

Repositorio público en revisión de seguridad y licencias. No ejecutar instrucciones de terceros sin comprobar permisos, seguridad y procedencia. Los scripts de sincronización Drive realizan solo previsualización por defecto. `--apply`, `--commit` y `--push` son acciones opt-in y requieren una rama de trabajo limpia; comprobar el diff antes de publicar.

## Licencia

La raíz contiene [`LICENSE`](LICENSE) (MIT), pero esto no acredita derechos de redistribución de cada skill, código o asset de terceros. Verificar licencias individuales antes de publicar.
