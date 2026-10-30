"""Genera public/og-cover.png (1200x630) — la imagen que se ve al compartir el sitio.

Uso:  npm run preview   (en otra terminal, puerto 4173)
      python scripts/make_og_image.py

Toma el render real del hero (no un mock): por eso captura sobre el preview server.
Luego hay que reconstruir (`npm run build`) para que quede también en docs/.
"""

from pathlib import Path

from playwright.sync_api import sync_playwright

# vite preview escucha en localhost (IPv6 ::1 en Windows); 127.0.0.1 falla.
URL = "http://localhost:4173"
OUT = Path(__file__).resolve().parent.parent / "public" / "og-cover.png"
W, H = 1200, 630

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    ctx = browser.new_context(
        viewport={"width": W, "height": H},
        device_scale_factor=2,
        reduced_motion="reduce",  # sin animaciones: todo el hero queda visible
    )
    ctx.add_init_script("localStorage.setItem('sa-theme','dark')")
    page = ctx.new_page()
    page.goto(URL, wait_until="networkidle")
    page.evaluate("document.fonts.ready")
    page.wait_for_timeout(600)

    # El hero mide más de 630 px de alto: se escala la página entera (CSS zoom)
    # para que header + hero entren completos en el marco 1200x630, sin cortes.
    scale = page.evaluate(
        """() => {
            const hero = document.querySelector('section[aria-labelledby="hero-title"]');
            const needed = hero.getBoundingClientRect().bottom + 12;
            const s = Math.min(1, %d / needed);
            document.documentElement.style.zoom = String(s);
            return s;
        }""" % H
    )
    page.wait_for_timeout(300)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(OUT), clip={"x": 0, "y": 0, "width": W, "height": H})
    browser.close()

print(f"escala aplicada: {scale:.3f}")

print(f"{OUT}  {OUT.stat().st_size/1024:.0f} KB  ({W*2}x{H*2} px, scale 2)")
