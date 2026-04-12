# Revelio

Web app radiology workflow con backend FastAPI e frontend statico servito dalla stessa applicazione.

## Struttura progetto

- `backend/` API FastAPI, logica dominio, seed dati, script smoke test.
- `frontend/` interfaccia web (HTML/CSS/JS) montata da FastAPI.

## Avvio locale (come in demo)

Prerequisiti: Python 3.11+.

1. Crea il virtual environment:
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
```
2. Installa dipendenze:
```bash
pip install -r requirements.txt
```
3. Crea configurazione locale:
```bash
cp .env.example .env
```
4. Avvia il server:
```bash
uvicorn app.main:app --reload
```
5. Apri nel browser:
- App: `http://127.0.0.1:8000/`
- API docs: `http://127.0.0.1:8000/docs`

## Credenziali seed per test

Definite in `backend/app/seed/seed_data.py`:

- `Amaggio` / `Alessiom92!` (Risonanza Magnetica)
- `Rmaselli` / `Robertom79!` (Tomografia Computerizzata)
- `Edipiero` / `Erikad98!` (Radiografia Tradizionale)

## Dati da cambiare se vuoi personalizzare i test

- Configurazione ambiente: `backend/.env`
  - `SECRET_KEY`
  - `ACCESS_TOKEN_EXPIRE_MINUTES`
  - `DEBUG`
  - `DATABASE_URL`
- Utenti di test e password seed: `backend/app/seed/seed_data.py`
  - `TECHNICIAN_DEFINITIONS`
- Dataset esami/sessioni seed: `backend/app/seed/seed_data.py`
  - `MACHINE_SHIFT_BLUEPRINTS`
  - `PATIENT_DEFINITIONS`

Dopo modifiche al seed, elimina `backend/revelio.db` e riavvia `uvicorn` per rigenerare dati coerenti.

## Cosa caricare su GitHub

Da caricare:
- codice sorgente (`backend/app`, `backend/scripts`, `frontend`)
- `backend/requirements.txt`
- `backend/.env.example`
- `README.md`
- `.gitignore`

Da NON caricare:
- `backend/.env` (segreti locali)
- `backend/.venv/` (virtual environment)
- `*.db` / `*.sqlite*` (database locale)
- `__pycache__/`, `*.pyc`
- file IDE/OS (`.DS_Store`, `.vscode/`)

## Smoke test rapido

Con server non avviato in parallelo:
```bash
backend/.venv/bin/python backend/scripts/smoke_test.py
```

## Test API con Postman

File pronti da importare:
- `backend/tests/postman/Revelio_API_Smoke_FSM.postman_collection.json`
- `backend/tests/postman/Revelio_Local.postman_environment.json`

Esecuzione:
1. Avvia backend con `uvicorn app.main:app --reload` da `backend/`.
2. Importa collection + environment in Postman.
3. Seleziona l'environment `Revelio Local`.
4. Esegui la collection in ordine (01..14).

La suite verifica autenticazione, worklist, regole FSM e vincoli di autorizzazione/turno.
Include anche i casi UC-06 di errore: `400` (CANCELLED senza nota), `403` (autorizzazione), `409` (transizione non valida).

## Pubblicazione su GitHub

1. Crea una repository vuota su GitHub (senza README iniziale).
2. Dalla root del progetto esegui:
```bash
git add -A
git commit -m "chore: clean repository and prepare secure GitHub release"
git branch -M main
git remote add origin <URL_REPO_GITHUB>
git push -u origin main
```
3. Condividi con il professore l'URL della repository.
