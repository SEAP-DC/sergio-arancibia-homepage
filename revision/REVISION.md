# Revisión de la Homepage — 30 de octubre de 2026

Alcance: revisión completa del sitio (`D:\Huaso_lalo\13 Homepage`) con mejoras.
**La sección Proyectos no se tocó** (`src/components/sections/Projects.tsx` y
`ProjectCard.tsx`): se midió y se reportan sus defectos, pero quedaron intactos.

Todos los defectos de abajo están medidos en el DOM (`getComputedStyle`,
`getBoundingClientRect`) o en la consola de red, no a ojo. Las capturas de
evidencia están en `revision/capturas/`.

---

## 1. Lo que estaba roto

### 1.1 El gráfico del hero se dibujaba vacío
Las 12 barras del "dashboard" del hero medían **0 px de alto**: el contenedor
flex hijo no tenía altura definida, así que el `height: 42%` de cada barra
resolvía contra 0.

| | alto de las barras |
|---|---|
| antes | `0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0` px |
| después | `47, 65, 39, 79, 71, 54, 90, 61, 40, 67, 43, 65` px |

Además el chip flotante "actualizado hace 5 min" (`top-16`) caía encima del
tercer KPI: movido al borde inferior de la tarjeta.

### 1.2 La copia offline salía sin estilos (esto es lo que se veía "en blanco")
Al abrir el HTML con doble clic (`file://`) el navegador trata la página como
origen `null` y bloquea dos cosas del build de Vite:

- `<script type="module">` externos → CORS de módulos ES
- `<link rel="stylesheet">` locales → CORS de hojas de estilo

Consola real de la copia anterior:

```
error: Access to CSS stylesheet at 'file:///.../offline/assets/index-B8aUNSnv.css'
       from origin 'null' has been blocked by CORS policy
error: Failed to load resource: net::ERR_FAILED
```

Sin CSS no hay colores, ni tipografías, ni layout: el sitio "no abre" aunque el
build esté perfecto. Solución: `scripts/build_offline.py` ahora incrusta JS, CSS
y las woff2 como `data:` dentro de `offline/index.html`.

| | CSS legible en la página | reglas CSS | peticiones externas |
|---|---|---|---|
| antes | bloqueada | 0 | — |
| después | embebido | 83 | 0 |

### 1.3 `npm run preview` no respondía en `127.0.0.1`
`vite preview` sin argumentos escucha solo en `localhost`, que en Windows
resuelve a IPv6 `::1`; `http://127.0.0.1:4173` rechazaba la conexión
(`curl: (7) ... Could not connect to server`). El script ahora fuerza
`--host 127.0.0.1 --port 4173 --strictPort` y ambas direcciones responden 200.

### 1.4 Contraste por debajo de AA en texto pequeño
Ratios calculados sobre la superficie real donde se usa cada token:

| token | antes | después | superficie |
|---|---|---|---|
| `--faint` oscuro | 3.46:1 | **4.74:1** | sobre `card-2` |
| `--faint` claro | 2.53:1 | **5.44:1** | sobre `card` |
| `--muted` claro | 5.84:1 | **7.02:1** | sobre `card` |
| `--accent-text` claro | 4.91:1 | **5.60:1** | sobre `card` |
| `--ink` (claro / oscuro) | 15.04:1 / 17.99:1 | sin cambio | sobre `bg` |

El umbral AA para texto pequeño es 4.5:1; `--faint` en ambos modos no lo cumplía.

### 1.5 Peticiones a un tercero (Google Fonts)
Se cargaban Inter y JetBrains Mono desde `fonts.googleapis.com`. Ahora están
autoalojadas en `src/assets/fonts/` (subset latin, woff2 variables) y el QA
afirma **cero peticiones fuera del origen** tanto en preview como en producción.

### 1.6 SEO y tarjeta social
No había canonical, ni OG, ni Twitter, ni JSON-LD, ni `theme-color` por modo, y
el `og:image` apuntaba a un archivo que no existía. Ahora: título y descripción
reales, canonical, `theme-color` claro/oscuro, OG/Twitter completos, JSON-LD
`Person` parseable, y portada generada con `scripts/make_og_image.py`
(2400×1260 px, 375.949 bytes servidos, verificado con `curl -sI`).
La portada anterior salía cortada a mitad de frase; el script ahora aplica
`zoom` al documento para que header + hero entren completos en el marco 1200×630
(escala aplicada: 0.805).

### 1.7 Accesibilidad de la navegación
- No había indicación de la sección activa → ahora `IntersectionObserver` en la
  franja central (`rootMargin: "-25% 0px -55% 0px"`) + `aria-current`.
- El botón del menú móvil apuntaba con `aria-controls` a un `id` que no existía
  mientras el menú estaba cerrado. Ahora el panel queda montado con `hidden`.
  QA: `ariaControlsRoto: 0`.
- El destino del enlace "Saltar al contenido" no era enfocable: `<main>` lleva
  `tabIndex={-1}`. El chequeo de teclado (foco visible) pasa.

### 1.8 Fragilidad del tema
- El fondo de partículas leía los colores del tema una sola vez y los cacheaba:
  al cambiar de tema el lienzo seguía con los colores viejos. Ahora observa el
  cambio de clase en `<html>` y relee; también escucha `prefers-reduced-motion`.
- `ThemeProvider` usaba `localStorage` sin protección: bajo `file://` o en modo
  privado lanza y tumba la app en el arranque. Ahora va envuelto en `try/catch`.

---

## 2. Qué se cambió, archivo por archivo

| archivo | cambio |
|---|---|
| `src/index.css` | tokens de contraste AA + `@font-face` de las fuentes locales |
| `src/assets/fonts/*.woff2` | Inter 400-700 y JetBrains Mono 400-600 (latin) |
| `index.html` | SEO/canonical/OG/Twitter/theme-color + JSON-LD `Person`; fuera Google Fonts |
| `src/data/content.ts`, `src/types/index.ts` | `email`, `emailDisplay`, `url`, `social` (GitHub) y tipo `SocialLink` |
| `src/components/sections/Header.tsx` | sección activa + `aria-current`, menú móvil montado con `hidden`, `ref` del botón |
| `src/components/sections/HeroPreview.tsx` | arreglo de las barras (0 px) y del chip sobre el KPI |
| `src/components/sections/Contact.tsx`, `Footer.tsx` | correo legible en pantalla + perfiles públicos desde `content.ts` |
| `src/components/ui/ThemeProvider.tsx` | `localStorage` protegido |
| `src/components/ui/NeuralBackground.tsx` | relee colores al cambiar tema, `reduced-motion`, limpieza de observers |
| `src/layouts/Layout.tsx` | `tabIndex={-1}` en `<main>` |
| `vite.config.ts` | `.nojekyll` con `import.meta.dirname` |
| `public/og-cover.png` | portada social 1200×630 @2x |
| `package.json` | scripts `lint`, `offline`, `verify`, `verify:offline`, `og`; `preview` fijado a 127.0.0.1:4173 |
| `.oxlintrc.json` | `ignorePatterns` en `docs/`, `dist/`, `offline/`; `no-unused-vars` en aviso |
| `.gitignore` | ignora `scripts/verify_out/` (capturas de trabajo) |
| `README.md` | reescrito para este proyecto (antes era el boilerplate de Vite) |
| `scripts/verify.py` | usa el origen bajo prueba (`HOMEPAGE_URL`); despliega animaciones antes de capturar; chequea OG, JSON-LD, `aria-current`, barras con altura y cero red externa |
| `scripts/build_offline.py` | incrusta JS + CSS + woff2 (`data:`) en `offline/index.html` |
| `scripts/make_og_image.py` | nueva portada social con ajuste de escala |
| `scripts/verify_offline.py` | nueva prueba `file://`: cero red, CSS embebido, tema, scroll |
| `_qa*/` | eliminados 7 scripts y 9 capturas QA temporales (los reemplazan `scripts/verify*.py`) |

---

## 3. Zona congelada: Proyectos

No se modificó nada. Un defecto medido ahí, para que decidas:

- En **modo oscuro**, las filas del visual de la tercera tarjeta ("Auditoría de
  datos panel") tienen relleno `rgb(13,17,23)` — idéntico al fondo de la tarjeta
  (`--card`) — de modo que solo se sostienen en el borde y la zona superior de la
  tarjeta se lee como una banda vacía.
- Arreglo de una línea (dentro de `ProjectCard.tsx`, en las filas del visual de
  auditoría): usar `dark:bg-card-2` en lugar del relleno actual. Las barras de la
  primera tarjeta ya usan ese patrón y se ven bien.

Dime si lo aplico y lo hago en un commit aparte.

---

## 4. QA reproducible y sus resultados

```
npm run lint              → oxlint sin avisos
npm run build             → tsc -b + vite build OK (166 ms)
npm run offline           → offline/ regenerada (5 entradas, 740 KB)
npm run verify            → RESULTADO: TODO OK   (contra 127.0.0.1:4173)
HOMEPAGE_URL=<produccion> npm run verify → RESULTADO: TODO OK
npm run verify:offline    → RESULTADO: offline OK (cero red)
```

Chequeos de `verify.py` (6 pasadas): escritorio claro, escritorio oscuro, móvil
390 px, `prefers-reduced-motion`, navegación por teclado, y SEO/nav (OG, JSON-LD
`Person`, `aria-current`, barras con altura, cero peticiones a terceros).

Pesos del build: JS 233.79 kB (gzip 72.98) · CSS 35.39 kB (gzip 7.32) ·
Inter 48.25 kB · JetBrains Mono 31.43 kB.

Capturas en esta carpeta: `desktop-light.png`, `desktop-dark.png`,
`mobile-light.png`, `seo-nav.png`, `offline-file.png`, `portada-social.png`.

---

## 5. Estado de la publicación

Commits en `main` ya publicados en GitHub Pages y verificados por polling del
título nuevo en la URL en vivo: `1f0a3cd` (sitio) y `3dc156e` (herramientas).
El commit `5c7202d` (arreglo del filtro de origen en `verify.py`) quedó
colgado en el primer intento de `git push`; se reintentó al cerrar esta revisión.
Este informe y sus capturas entran en un commit final aparte.
