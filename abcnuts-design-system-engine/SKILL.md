---
name: design-system-engine
description: Build a coherent, premium, single-team visual system for any frontend instead of designing screens individually. Create design tokens, a component library, and enforce design coherence, accessibility, responsive behavior and art direction. Use before building UI so every screen looks like one product.
type: meta-skill
---

# Design System Engine

**Meta-Skill** para construir un sistema visual global coherente y premium antes de diseñar cada pantalla. Evita el aspecto de "template generado por IA".

## Overview

Diseña un **sistema**, no pantallas sueltas. Define tokens + componentes + reglas de coherencia, y luego aplícalos a toda la interfaz para que parezca creada por **un solo equipo de producto**.

## 1. Design Tokens

Define: colors · semantic colors · typography · spacing · radius · shadows · borders · gradients · motion · breakpoints · z-index · surfaces · density.

Los colores deben tener **función semántica** (success/error/warning/info/primario/secundario), no ser arbitrarios.

## 2. Component Library

Como mínimo cuando correspondan:

```
Button  IconButton  Input  Textarea  Select  Checkbox  Radio  Switch
Badge  Avatar  Card  Dialog  Drawer  Sheet  Tooltip  Popover  Dropdown
Tabs  Accordion  Navigation  Breadcrumbs  Pagination  Table  DataTable
Form  Toast  Alert  Progress  Skeleton  EmptyState  ErrorState
CommandPalette  Search  Sidebar  Header  Footer  Modal
```

Usa una UI library sólida (shadcn/ui, Radix, MUI, Chakra, Ant Design, Headless UI) **sin mezclar** arbitrariamente.

## 3. Frontend Premium

Prioridades: jerarquía · claridad · composición · ritmo visual · navegación · responsive · microinteracciones · accesibilidad · velocidad · personalidad.

Evita: dashboards genéricos · exceso de cards · gradientes sin propósito · glassmorphism indiscriminado · sombras excesivas · tipografías mezcladas sin sistema · animaciones gratuitas · páginas idénticas.

## 4. Accessibility

Semantic HTML · keyboard navigation · visible focus · ARIA solo cuando sea necesario · contraste · labels · alt text · reduced motion · screen-reader compatible · focus management · touch targets · estados no solo por color. Objetivo **WCAG 2.2 AA** cuando aplicable.

## 5. Responsive

Probar: 320 · 375 · 390 · 430 · 768 · 1024 · 1280 · 1440 · 1920+. Verificar overflow, navegación, modales, tablas, imágenes, tipografía, touch targets, formularios, scroll, sticky.

## 6. Art Direction — HyperRender

Cuando haya identidad artística/premium: construye identidad visual propia (no solo gradient+glass). Considera GSAP, Three.js, WebGL, GLSL, Canvas, Framer Motion, custom shaders, particle systems, noise fields, parallax, scroll-driven animation. **PERFORMANCE > EFECTO GRATUITO.** Respeta `prefers-reduced-motion`, memory-leak-free, cleanup/disposal, DPR control.

Prefiere **sistemas generativos reproducibles** (seeds, noise determinista) sobre imágenes aleatorias.

## 7. Design Coherence Engine

Antes de terminar, verifica:
- **Visual**: ¿todas las páginas parecen del mismo producto?
- **Typography**: ¿escala tipográfica consistente?
- **Color**: ¿función semántica?
- **Components**: ¿se reutilizan?
- **Motion**: ¿gramática común?
- **Content**: ¿tono coherente?
- **Navigation**: ¿arquitectura de información consistente?

Pregunta final: **"¿Esto parece realmente un producto premium o parece generado automáticamente?"** Si parece generado → refactoriza.

## Dependencies

- Leer `MASTER-AGENT.md` (secciones 8-12, 25-30) para las reglas completas.
- Usar junto a `project-maximizer`.

## Notas

- No diseñes pantallas sueltas sin sistema previo.
- Marca branding provisional como `PROVISIONAL — OWNER REVIEW REQUIRED`.
- No bloquees el desarrollo por decisiones estéticas menores; usa defaults profesionales.
