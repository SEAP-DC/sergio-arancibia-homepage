"""Regenera la copia offline del sitio (carpeta `offline/`) desde el build.

Uso:
    npm run build && npm run offline
    (o: python scripts/build_offline.py)

Por qué hace falta: al abrir un HTML con doble clic (protocolo `file://`) el
navegador trata la página como origen `null` y bloquea dos cosas del build:
  1. los `<script type="module">` externos  -> CORS de módulos ES
  2. las `<link rel="stylesheet">` locales  -> CORS de hojas de estilo
     (y con el CSS se pierden colores, layout y tipografías)
El sitio se ve "roto" o sin estilos aunque el build esté perfecto.

Qué hace entonces, sobre una copia de `docs/`:
  1. incrusta el JS del bundle dentro de `index.html`;
  2. incrusta el CSS dentro de `index.html` y convierte las tipografías woff2 a
     `data:` (base64) para que no dependan de leer archivos al lado;
  3. deja favicon, og-cover.png y el resto de estáticos junto al HTML.

Resultado: un `offline/index.html` que se abre con doble clic, sin servidor y
sin red. No toca el código fuente ni el despliegue de GitHub Pages.
"""

from __future__ import annotations

import base64
import mimetypes
import re
import shutil
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "docs"
DST = ROOT / "offline"

MODULE_SCRIPT = re.compile(
    r'<script type="module"[^>]*\bsrc="(?P<src>[^"]+)"[^>]*>\s*</script>'
)
STYLESHEET = re.compile(
    r'<link[^>]*\brel="stylesheet"[^>]*\bhref="(?P<href>[^"]+)"[^>]*>'
)
CSS_URL = re.compile(r"url\(\s*['\"]?(?P<url>[^'\")]+)['\"]?\s*\)")

README = """# Copia offline de la Homepage (13 Homepage)

Copia autocontenida del build, para revisarla **sin internet y sin servidor**:
se abre con doble clic.

- `index.html` — el sitio con el **JS y el CSS incrustados dentro**, y las
  tipografías Inter / JetBrains Mono en `data:` (base64). Así no choca con el
  bloqueo CORS que el navegador aplica a módulos ES y hojas de estilo locales
  bajo protocolo `file://`, que es lo que dejaba la copia anterior sin estilos.
- `og-cover.png`, favicon y demás estáticos — al lado, con rutas relativas.

## Cómo abrirla

Doble clic en **index.html** — o arrástrala a cualquier navegador.

## Regenerarla tras cambiar el código

```bash
npm run build && npm run offline
```

(el script es `scripts/build_offline.py`; no editar esta carpeta a mano, se
borra y se vuelve a crear completa)

Copia generada el {fecha}.
"""


def to_data_uri(path: Path) -> str | None:
    if not path.exists():
        return None
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    if path.suffix.lower() == ".woff2":
        mime = "font/woff2"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"


def embed_css(css_path: Path) -> str | None:
    """CSS listo para meter en un <style>: tipografías como data: URI."""
    if not css_path.exists():
        return None
    css = css_path.read_text(encoding="utf-8")

    def repl(match: re.Match[str]) -> str:
        url = match.group("url")
        if url.startswith(("data:", "http://", "https://")):
            return match.group(0)
        data = to_data_uri((css_path.parent / url).resolve())
        return f"url('{data}')" if data else match.group(0)

    return CSS_URL.sub(repl, css)


def main() -> int:
    if not (SRC / "index.html").exists():
        print("ERROR: no existe docs/index.html — ejecuta primero `npm run build`.", file=sys.stderr)
        return 1

    if DST.exists():
        shutil.rmtree(DST)
    shutil.copytree(SRC, DST)

    html_path = DST / "index.html"
    html = html_path.read_text(encoding="utf-8")

    avisos: list[str] = []

    def inline_script(match: re.Match[str]) -> str:
        rel = match.group("src").lstrip("./")
        js_path = DST / rel
        if not js_path.exists():
            avisos.append(f"no se encontró {rel}; se deja el <script> externo")
            return match.group(0)
        code = js_path.read_text(encoding="utf-8")
        # evita cerrar el <script> antes de tiempo si el bundle trae "</script>"
        code = code.replace("</script", "<\\/script")
        js_path.unlink()
        return f'<script type="module">\n{code}\n</script>'

    def inline_style(match: re.Match[str]) -> str:
        rel = match.group("href").lstrip("./")
        css_path = DST / rel
        css = embed_css(css_path)
        if css is None:
            avisos.append(f"no se encontró {rel}; se deja el <link> externo")
            return match.group(0)
        css_path.unlink()
        return f"<style>\n{css}\n</style>"

    html, n_js = MODULE_SCRIPT.subn(inline_script, html, count=1)
    html, n_css = STYLESHEET.subn(inline_style, html, count=1)
    if n_js == 0:
        avisos.append("no se encontró el <script> de módulo; el build cambió de formato")
    if n_css == 0:
        avisos.append("no se encontró el <link> de estilos; el build cambió de formato")

    # localStorage puede estar bloqueado bajo file://: el index.html ya trae try/catch.
    html_path.write_text(html, encoding="utf-8")

    # las woff2 ya viajaban dentro del CSS como data:; si nada las apunta, sobran
    if "assets/" not in html:
        for leftover in (DST / "assets").glob("*.woff2"):
            leftover.unlink()
    (DST / "README.md").write_text(README.format(fecha=date.today().isoformat()), encoding="utf-8")

    for aviso in avisos:
        print(f"ADVERTENCIA: {aviso}", file=sys.stderr)

    total = sum(p.stat().st_size for p in DST.rglob("*") if p.is_file())
    print(f"offline/ regenerada: {len(list(DST.rglob('*')))} entradas, {total/1024:.0f} KB en total.")
    for p in sorted(DST.rglob("*")):
        if p.is_file():
            print(f"  {p.relative_to(ROOT)}  {p.stat().st_size/1024:.1f} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
