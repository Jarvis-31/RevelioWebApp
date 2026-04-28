#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
VENV_DIR="$BACKEND_DIR/.venv"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Errore: python3 non trovato. Installa Python 3.11+ e riprova."
  exit 1
fi

cd "$BACKEND_DIR"

if [ ! -d "$VENV_DIR" ]; then
  echo "Creo virtual environment..."
  python3 -m venv "$VENV_DIR"
fi

VENV_PYTHON="$VENV_DIR/bin/python"

echo "Installo/aggiorno dipendenze..."
"$VENV_PYTHON" -m pip install -r requirements.txt

if [ ! -f ".env" ]; then
  echo "Creo backend/.env da backend/.env.example..."
  cp .env.example .env
fi

echo
echo "Revelio avviato su http://127.0.0.1:8000/"
echo "API docs: http://127.0.0.1:8000/docs"
echo

"$VENV_PYTHON" -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
