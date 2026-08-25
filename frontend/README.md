# Angular frontend for the Ollama chatbot

This is the Angular (v20, standalone components, SCSS) re-implementation of the
previous HTML/CSS/JS frontend. It is built to `dist/frontend/browser/` and served
directly by the existing Flask backend (see `app.py` - `home()` serves
`index.html` and `baseHref` is `/static/`, so bundles are served by Flask's static
route while all `/chat-stream`, `/sessions`, etc. API endpoints remain unchanged).

## Requirements
- Node.js 18.19+ and npm (Angular 20 requires Node 18.19+ / 20.11+)

## Build
```bash
cd frontend
npm install
npm run build          # production build -> dist/frontend/browser
```

## Run (integrated with Flask)
```bash
# from project root (side of app.py)
python app.py
# open http://127.0.0.1:5000/
```

The Angular app is now the UI served at `/`; the old `templates/index.html` and
`static/` files remain untouched on disk as the previous frontend.

## Dev mode (optional, hot reload)
```bash
cd frontend
ng serve              # serves on http://localhost:4200 with in-memory build
```
Note: dev-server mode needs the Flask API at `/`; if using `ng serve` alone,
the API calls would 404 unless Flask runs on the same origin or a proxy is added.
For the integrated setup, production build + Flask is the supported path.

## Notes
- `marked` and `highlight.js` replace the old CDN tags.
- Session pin/archive/rename/delete/clear and streaming chat are implemented as
  services (`chat.service.ts`, `session.service.ts`, `markdown.service.ts`).
- Streaming uses fetch + ReadableStream (same semantics as the old script.js).