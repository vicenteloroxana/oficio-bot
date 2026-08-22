# oficio-bot
Bot de Telegram para trabajadores de oficio — que contemple el ciclo completo de presupuesto → seña → cobro → recordatorio de mora, sin salir de Telegram.

## Deploy en Railway

El bot corre en **polling** en local y cambia solo a **webhook** cuando
detecta que está en Railway (ver [`main.py`](main.py) y
[ADR-001](docs/adr/001-stack-tecnologico.md)) — no hay nada que configurar
a mano para elegir el modo.

Pasos para deployar:

1. Crear el proyecto en Railway y conectarlo al repo de GitHub (deploy
   automático en cada push a `main`).
2. Generar un dominio público para el servicio (Settings → Networking →
   Generate Domain). Esto hace que Railway inyecte `RAILWAY_PUBLIC_DOMAIN`
   automáticamente — es la señal que usa `main.py` para arrancar en modo
   webhook.
3. Cargar las variables de entorno del bot en el dashboard (Variables),
   usando [`.env.example`](.env.example) como referencia:
   `TELEGRAM_BOT_TOKEN`, `REMINDER_DAYS`, `MAX_LOGO_SIZE_MB`, `PDF_DIR`,
   `DB_PATH` (ver punto siguiente).
4. **Agregar un Volume** (Settings → Volumes) montado en `/data`. El
   filesystem de Railway es efímero por default: sin Volume, la base
   SQLite y los PDFs generados se pierden en cada redeploy. Con el Volume
   montado, setear:
   ```
   DB_PATH=/data/oficio_bot.db
   PDF_DIR=/data/pdfs
   ```
5. Push a `main` → Railway builda con Nixpacks y arranca con el comando de
   [`railway.toml`](railway.toml).
