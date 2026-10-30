"""Prueba la copia offline (`offline/index.html`) abriendola por file://.

Demuestra que el sitio funciona sin red:
  - todas las peticiones son file:// (cero dependencias externas)
  - las tipografías Inter / JetBrains Mono están cargadas
  - las secciones principales tienen contenido visible
  - el conmutador de tema responde sin tocar la red

Uso:
    npm run build && npm run offline && npm run verify:offline
Salida 0 si todo pasa, 1 si algo falla.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "offline" / "index.html"
SHOT = ROOT / "scripts" / "verify_out" / "offline-file.png"

MARKERS = ["Sergio Arancibia", "Qué hago", "Trayectoria", "Proyectos", "Hablemos"]


def main() -> int:
    if not PAGE.exists():
        print("ERROR: no existe offline/index.html — ejecuta `npm run offline`.", file=sys.stderr)
        return 1

    requests: list[str] = []
    errors: list[str] = []
    checks: dict[str, object] = {}

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.on("request", lambda r: requests.append(r.url))
        page.on("pageerror", lambda e: errors.append(str(e)[:200]))

        page.goto(PAGE.as_uri(), wait_until="networkidle")
        page.wait_for_timeout(400)

        checks["peticiones_externas"] = sorted(
            {u for u in requests if not u.startswith(("file://", "data:"))}
        )
        checks["tipografias"] = page.evaluate(
            """() => {
                const ok = (f, w) => document.fonts.check(`${w} 16px ${f}`);
                return { inter400: ok('Inter','400'), inter700: ok('Inter','700'),
                         mono400: ok('JetBrains Mono','400') };
            }"""
        )
        text = page.evaluate("() => document.body.innerText")
        checks["secciones_visibles"] = {m: (m in text) for m in MARKERS}
        checks["css_embebida"] = page.evaluate(
            """() => {
                const styles = document.querySelectorAll('style').length;
                let reglas = 0;
                for (const s of document.styleSheets) {
                    try { reglas += s.cssRules.length; } catch { /* bloqueada por CORS */ }
                }
                return { etiquetasStyle: styles, reglasCSS: reglas,
                         hayLinkExterno: [...document.querySelectorAll('link[rel="stylesheet"]')].length };
            }"""
        )
        checks["barras_hero_px"] = page.evaluate(
            """() => [...document.querySelectorAll('[aria-label^="Vista previa"] .h-28 > div > div')]
                   .map(d => Math.round(d.getBoundingClientRect().height))"""
        )

        antes = page.evaluate("() => document.documentElement.className")
        page.evaluate(
            """() => {
                const b = [...document.querySelectorAll('header button')]
                    .find(x => /cambiar a modo/i.test(x.getAttribute('aria-label') || ''));
                if (b) b.click();
            }"""
        )
        page.wait_for_timeout(250)
        checks["tema"] = f"{antes!r} -> {page.evaluate('() => document.documentElement.className')!r}"

        page.mouse.wheel(0, 20000)
        page.wait_for_timeout(400)
        checks["scroll_ok"] = page.evaluate("() => window.scrollY > 100")

        SHOT.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(SHOT))
        browser.close()

    checks["errores_js"] = errors
    fallos: list[str] = []
    if checks["peticiones_externas"]:
        fallos.append(f"peticiones externas: {checks['peticiones_externas']}")
    if errors:
        fallos.append(f"errores de consola: {errors}")
    if not all(checks["tipografias"].values()):  # type: ignore[union-attr]
        fallos.append(f"tipografías no cargadas: {checks['tipografias']}")
    if not all(checks["secciones_visibles"].values()):  # type: ignore[union-attr]
        faltan = [k for k, v in checks["secciones_visibles"].items() if not v]  # type: ignore[union-attr]
        fallos.append(f"secciones sin contenido: {faltan}")
    if not checks["barras_hero_px"]:
        fallos.append("no se encontró el gráfico del hero")
    if not checks["css_embebida"]["reglasCSS"] or checks["css_embebida"]["hayLinkExterno"]:
        fallos.append(f"CSS no embebido/legible: {checks['css_embebida']}")
    if checks["tema"].split(" -> ")[0] == checks["tema"].split(" -> ")[1]:
        fallos.append("el conmutador de tema no cambió nada")
    if not checks["scroll_ok"]:
        fallos.append("el scroll no avanzó")

    print(json.dumps(checks, ensure_ascii=False, indent=2))
    print("captura:", SHOT)
    if fallos:
        print("RESULTADO: FALLOS")
        for f in fallos:
            print(" -", f)
        return 1
    print("RESULTADO: offline OK (cero red)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
