# Backend variants and runtime source of truth

## Production/dev default backend
- Use the modular backend under `backend/app/` with entrypoint `backend/run.py`.
- Main compose file: `backend/docker-compose.yml`.

## Legacy/experimental backends
- `backend/Prototipo_Excel/`
- Files with suffix `1.py` under `backend/app/routes/` and `backend/app/services/`
- `backend/docker-compose1.yml`

These legacy variants are kept only for historical reference and local experiments.
Do not use them as the default runtime path for frontend integration.
