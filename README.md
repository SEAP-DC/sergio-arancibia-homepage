# 13 Homepage — sitio personal de Sergio Arancibia

Página de una sola página (One Page) para captar clientes de análisis de datos:
limpieza de datos con Stata, automatización con Python y dashboards.

- **En vivo:** <https://seap-dc.github.io/sergio-arancibia-homepage/>
- **Stack:** React 19 + TypeScript + Vite 7 + Tailwind CSS 4, sin backend.
- **Despliegue:** la rama `main` publica la carpeta `docs/` en GitHub Pages
  (`vite.config.ts` fija `base` y el build deja `.nojekyll`).

## Cómo ver el sitio

| Quiero… | Comando |
|---|---|
| editar en caliente | `npm run dev` (puerto 5173) |
| ver el build final | `npm run build && npm run preview` → <http://127.0.0.1:4173> |
| revisar sin servidor ni red | abrir `offline/index.html` con doble clic |

> **Por qué a veces "no abre":**
> 1. `vite preview` por defecto escucha solo en `localhost` (que en Windows
>    resuelve a IPv6 `::1`), así que `http://127.0.0.1:4173` rechaza la conexión.
>    El script `preview` ya fuerza `--host 127.0.0.1 --port 4173 --strictPort`
>    para que ambas formas funcionen.
> 2. `docs/index.html` **no** se puede abrir con doble clic: bajo `file://` el
>    navegador bloquea por CORS los módulos ES y las hojas de estilo locales, y
>    el sitio queda sin estilos. Para abrir sin servidor existe `offline/`, que
>    lleva JS, CSS y tipografías incrustados dentro del HTML.
> 3. Si el puerto está ocupado, `--strictPort` hace que falle en vez de cambiarse
>    solo:
>    `powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort 4173 -State Listen | Select-Object -Expand OwningProcess | ForEach-Object { Stop-Process -Id $_ -Force }"`.

## Scripts

```bash
npm run dev            # desarrollo con recarga
npm run build          # tsc -b + vite build  -> docs/
npm run preview        # sirve docs/ en 127.0.0.1:4173
npm run lint           # oxlint
npm run offline        # regenera offline/ a partir de docs/
npm run verify         # QA visual (Playwright) sobre el preview
npm run verify:offline # prueba offline/index.html abierto por file://
npm run og             # genera public/og-cover.png (portada 1200x630)
```

`verify`, `verify:offline` y `og` necesitan un Python con **Playwright**
instalado (aquí se usa el entorno del proyecto 09):

```bash
"D:/Huaso_lalo/09 precios/.venv/Scripts/python.exe" scripts/verify.py
```

`verify.py` espera el sitio servido en `http://localhost:4173`; se puede apuntar
a otro con la variable `HOMEPAGE_URL`. Sus capturas caen en `scripts/verify_out/`.
`og` requiere el preview levantado en otra terminal.

## Qué comprueba `scripts/verify.py`

Escritorio claro y oscuro · móvil (390 px) · `prefers-reduced-motion` · navegación
por teclado (foco visible y enlace "Saltar al contenido") · etiquetas `og:*`,
JSON-LD, `aria-current` de la navegación, que las barras del hero tengan altura y
que **no haya peticiones a terceros**. Si algo falla sale `RESULTADO: FALLOS`.

## Informe de la última revisión

`revision/REVISION.md` — qué estaba roto (con la medición que lo prueba), qué se
cambió archivo por archivo, los resultados del QA y la zona congelada. Sus
capturas de evidencia están en `revision/capturas/`.

## Dónde se edita el contenido

Todo el texto vive en `src/data/content.ts` (hero, servicios, trayectoria, stats,
proyectos, preguntas frecuentes y contacto). Los visuales de los proyectos son
**gráficos hechos con CSS**, no imágenes: no hay `public/img`.

Tipografías: Inter y JetBrains Mono autoalojadas en `src/assets/fonts/` (el sitio
no pide nada a Google Fonts). Colores y tokens de tema: `src/index.css`.

> La sección **Proyectos** (`src/components/sections/Projects.tsx` y
> `ProjectCard.tsx`) está congelada: no se modifica salvo pedido explícito.

## Puesta a punto tras un cambio

```bash
npm run lint && npm run build && npm run offline
npm run preview                     # en otra terminal
npm run verify                      # con el python de Playwright
git add -A && git commit -m "…" && git push    # Pages publica docs/
```
