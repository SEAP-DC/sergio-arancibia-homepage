# Copia offline de la Homepage (13 Homepage)

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

Copia generada el 2026-10-30.
