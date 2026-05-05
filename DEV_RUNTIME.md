# WireBot dev runtime quick guide

## Default runtime path
- Frontend: `npm run dev` (proxy `/api`).
- Backend (recommended): `npm run backend` using `backend/docker-compose.yml`.

By default, the recommended backend compose exposes `5005` on host.
Set `VITE_PROXY_TARGET` if you run the backend in another port.

## Useful frontend commands
- `npm run dev:docker` -> proxy to `http://127.0.0.1:5005`
- `npm run dev:local` -> proxy to `http://127.0.0.1:5000`

## Useful backend commands
- `npm run backend` / `npm run backend:down` (modular backend)
- `npm run backend:legacy` / `npm run backend:legacy:down` (legacy only)

## Pre-release smoke tests
- `npm run smoke`

## RAG (recuperación desde Excel)

The chat does **not** dump the whole spreadsheet into the model. It retrieves the **top `RAG_TOP_K` rows** that are most similar to the user question (embeddings + FAISS). Increase `RAG_TOP_K` (env, default `100` in `Config`) if you need more context; very high values increase prompt size and Ollama latency.

If you see the model say it is analyzing "5 rows", that is usually a **hallucination** or an old deployment; the real count is the numbered cases in `contexto_usado` from `/chat`.

## Ollama on the host (not the Flask container)

The backend calls Ollama at `OLLAMA_URL` (default `http://host.docker.internal:11434`). The Flask `docker-compose` service does **not** start Ollama; you run Ollama on Windows and tune it there.

### CPU threads (e.g. Ryzen with 8 physical cores)

Set before starting Ollama (User or System environment variables, or a wrapper script):

```text
OLLAMA_NUM_THREAD=8
```

Adjust if your CPU has a different physical core count. This limits threading for the Ollama process on the host; it is **not** read by the WireBot Flask app.

### Integrated GPU (AMD / other)

Whether Ollama can use an integrated GPU depends on the Ollama build, drivers, and OS support. Configure acceleration on the machine where `ollama serve` runs; the WireBot repo only connects over HTTP to `OLLAMA_URL`.

### Note

Do not add `OLLAMA_NUM_THREAD` to `backend/.env` expecting the Flask container to apply it to Ollama—Ollama runs outside that container unless you add a dedicated `ollama` service to compose later.
