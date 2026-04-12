# Guida Completa del Progetto Revelio

## Come leggere questa guida
Questa guida spiega:
- ogni cartella;
- ogni file presente nel progetto;
- il codice in modo "riga per riga" (nei file lunghi le righe sono raggruppate in blocchi logici, così resta comprensibile).

Linguaggio semplice: l'obiettivo è farti capire il progetto davvero, non impressionarti con parole difficili.

---

## 1) Struttura generale del progetto

### Cartella root (`/`)
Contiene i file principali di configurazione/documentazione e le due macro aree:
- `backend/` (API FastAPI + logica + database + seed)
- `frontend/` (interfaccia web: HTML/CSS/JS)

### Cartella `backend/`
Contiene tutto il lato server:
- API REST
- autenticazione
- modelli dati
- logica business (worklist, FSM esami)
- seed dati demo
- script di test rapido

### Cartella `frontend/`
Contiene tutto il lato client:
- pagina HTML di bootstrap
- logica UI in JavaScript vanilla
- styling in CSS
- immagini della web app

---

## 2) Elenco completo file + funzione

### Root
- `.gitignore`: dice a Git quali file NON versionare.
- `README.md`: istruzioni rapide per avvio, seed, pubblicazione GitHub.
- `GUIDA_COMPLETA_PROGETTO_REVELIO.md`: questa guida.

### Backend
- `backend/.env`: configurazione locale reale (segreti inclusi).
- `backend/.env.example`: template sicuro senza segreti reali.
- `backend/requirements.txt`: dipendenze Python.
- `backend/revelio.db`: database SQLite locale.
- `backend/scripts/smoke_test.py`: test end-to-end automatico rapido.

### Backend app (`backend/app`)
- `__init__.py`: export servizi principali.
- `main.py`: entrypoint FastAPI + mount frontend + seed startup.

#### API
- `api/__init__.py`: file segnaposto package.
- `api/v1/__init__.py`: file segnaposto package.
- `api/v1/api.py`: router principale API v1.
- `api/v1/endpoints/__init__.py`: file segnaposto package.
- `api/v1/endpoints/auth.py`: login e profilo utente loggato.
- `api/v1/endpoints/machines.py`: lista macchine + worklist per macchina.
- `api/v1/endpoints/exams.py`: dettaglio esame, audit, transizioni FSM.

#### Core
- `core/__init__.py`: file segnaposto package.
- `core/config.py`: lettura config da `.env`.
- `core/exceptions.py`: eccezioni custom applicative.
- `core/security.py`: hash password + JWT.
- `core/time.py`: utility date/ora con timezone Europe/Rome.

#### DB
- `db/__init__.py`: file segnaposto package.
- `db/session.py`: engine SQLAlchemy, sessioni DB, dependency `get_db`.
- `db/base.py`: import centralizzato modelli per metadata/tabelle.

#### Dependencies
- `dependencies/__init__.py`: export dependency auth.
- `dependencies/auth.py`: legge token Bearer e risolve tecnico corrente.

#### Models (ORM SQLAlchemy)
- `models/__init__.py`: export modelli.
- `models/enums.py`: enum MachineCode/SessionStatus/ExamStatus.
- `models/machine.py`: tabella macchine.
- `models/technician.py`: tabella tecnici.
- `models/session.py`: tabella sessioni turno.
- `models/patient.py`: tabella pazienti.
- `models/exam.py`: tabella esami + regole FSM.
- `models/exam_audit_event.py`: tabella storico transizioni.

#### Repositories
- `repositories/__init__.py`: export repository.
- `repositories/technician_repository.py`: query tecnici.
- `repositories/machine_repository.py`: query macchine.
- `repositories/session_repository.py`: query sessioni/turni.
- `repositories/exam_repository.py`: query esami + update stato.
- `repositories/audit_repository.py`: query/insert audit eventi.

#### Schemas (Pydantic)
- `schemas/__init__.py`: export schemi.
- `schemas/common.py`: basi comuni response/error.
- `schemas/auth.py`: request/response login.
- `schemas/audit.py`: payload eventi audit.
- `schemas/session.py`: payload sessioni.
- `schemas/machine.py`: payload macchine/worklist.
- `schemas/exam.py`: payload dettaglio/transizione esame.

#### Seed
- `seed/__init__.py`: export seed public.
- `seed/seed_data.py`: crea/aggiorna dati demo coerenti con turno orario.

#### Services
- `services/__init__.py`: export servizi usati dal package.
- `services/auth_service.py`: autenticazione utente.
- `services/worklist_service.py`: costruzione worklist macchina.
- `services/exam_state_service.py`: regole FSM e autorizzazioni transizioni.

### Frontend
- `frontend/index.html`: shell HTML minimale + link CSS/JS/font.
- `frontend/app.js`: logica completa UI, routing client, fetch API, rendering.
- `frontend/styles.css`: stile completo e responsive.
- `frontend/images/favicon.svg`: favicon.
- `frontend/images/Risonanza magnetica.jpg`: immagine macchina RM.
- `frontend/images/Tomografia computerizzata.png`: immagine macchina TC.
- `frontend/images/Radiografia.png`: immagine macchina RX.

---

## 3) Spiegazione file per file (riga per riga in blocchi)

## Root

### `.gitignore` (42 righe)
A cosa serve: evita di caricare su GitHub file sensibili o inutili (venv, db locale, cache, segreti).

Righe:
- 1-3: ignora file di sistema OS (`.DS_Store`, `Thumbs.db`).
- 5-8: ignora cartelle IDE/editor (`.vscode`, `.idea`, ecc.).
- 10-18: ignora cache/build Python (`__pycache__`, `.pyc`, ecc.).
- 20-23: ignora virtualenv locali.
- 25-30: ignora file `.env` reali, ma mantiene `.env.example`.
- 32-36: ignora DB locali e log runtime.
- 38-42: ignora output build generici (`dist`, `node_modules`, ecc.).

### `README.md` (93 righe)
A cosa serve: guida rapida per avvio locale e pubblicazione.

Righe:
- 1-6: descrizione progetto e struttura base.
- 8-29: setup locale (`venv`, install, `.env`, `uvicorn`).
- 31-39: credenziali demo seed.
- 41-54: quali dati cambiare per test personalizzati.
- 56-71: cosa caricare e cosa non caricare su GitHub.
- 73-77: smoke test rapido.
- 79-93: passaggi push su repository GitHub.

### `backend/.env` (10 righe)
A cosa serve: configurazione reale locale (da NON pubblicare).

Righe:
- 1-4: metadati app e modalità debug.
- 6: URL DB SQLite locale.
- 8-10: parametri JWT (chiave segreta, algoritmo, durata token).

### `backend/.env.example` (11 righe)
A cosa serve: template condivisibile sicuro.

Righe:
- 1-6: stesse chiavi base del `.env` reale.
- 8: placeholder `SECRET_KEY` da sostituire.
- 9-10: algoritmo e durata token.

### `backend/requirements.txt` (38 righe)
A cosa serve: lista librerie Python installate nel backend.

Righe:
- 1-38: dipendenze pin-rate con versione fissa (FastAPI, SQLAlchemy, Pydantic, Uvicorn, librerie JWT/password, ecc.).

### `backend/revelio.db`
A cosa serve: database SQLite locale già popolato.

Non è testo riga-per-riga (file binario). Contiene tabelle:
- `technicians`
- `machines`
- `sessions`
- `patients`
- `exams`
- `exam_audit_events`

Relazioni principali:
- `sessions.machine_id -> machines.id`
- `sessions.technician_id -> technicians.id`
- `exams.session_id -> sessions.id`
- `exams.patient_id -> patients.id`
- `exam_audit_events.exam_id -> exams.id`
- `exam_audit_events.performed_by_technician_id -> technicians.id`

---

## Backend app

### `backend/app/__init__.py`
A cosa serve: esporta servizi per import comodi dal package `app`.

Righe:
- 1-3: import classi `AuthService`, `ExamStateService`, `WorklistService`.
- 5-9: `__all__` definisce export ufficiali.

### `backend/app/main.py`
A cosa serve: avvia FastAPI, crea tabelle, seeda dati, monta frontend statico.

Righe:
- 1-14: import base (FastAPI, router API, DB, seed, filesystem path).
- 16-28: `lifespan` startup/shutdown app:
  - crea schema tabelle;
  - apre sessione DB;
  - esegue `seed_database`;
  - chiude sessione.
- 30-35: istanza `FastAPI` con title/version/debug/lifespan.
- 37: monta router API con prefisso v1.
- 40-42: endpoint `/health` per check stato.
- 45-52: se esiste `frontend/`, serve file statici su `/`.

---

## API

### `backend/app/api/__init__.py`
- Riga 1: file vuoto, serve solo a marcare package Python.

### `backend/app/api/v1/__init__.py`
- Riga 1: file vuoto, marca package versione API.

### `backend/app/api/v1/endpoints/__init__.py`
- Riga 1: file vuoto, marca package endpoint.

### `backend/app/api/v1/api.py`
A cosa serve: centralizza endpoint v1.

Righe:
- 1-5: import `APIRouter` e i router endpoint (`auth`, `machines`, `exams`).
- 7: crea `api_router`.
- 8-10: include i 3 router nel router principale.

### `backend/app/api/v1/endpoints/auth.py`
A cosa serve: login e profilo utente corrente.

Righe:
- 1-15: import FastAPI/DB/eccezioni/schemi/servizio auth.
- 16: crea router `/auth`.
- 19-33: metadata endpoint `POST /auth/login` (response e codici errore).
- 34-63: funzione `login`:
  - riceve username/password;
  - chiama `AuthService.authenticate`;
  - mappa eccezioni in HTTP 401/403;
  - ritorna token + tecnico.
- 66-80: metadata endpoint `GET /auth/me`.
- 81-84: funzione `me`, restituisce tecnico autenticato.

### `backend/app/api/v1/endpoints/machines.py`
A cosa serve: dashboard macchine e worklist macchina.

Righe:
- 1-12: import dipendenze, enum macchina, schemi e `WorklistService`.
- 13: router `/machines`.
- 16-26: metadata `GET /machines`.
- 27-33: `list_machines`, richiede auth e ritorna macchine attive.
- 35-49: metadata `GET /machines/{machine_code}/worklist`.
- 50-63: `get_machine_worklist`, ritorna worklist o 404 se macchina inesistente.

### `backend/app/api/v1/endpoints/exams.py`
A cosa serve: dettaglio esame, audit e transizioni FSM.

Righe:
- 1-21: import (eccezioni business, schemi, servizio esami).
- 22: router `/exams`.
- 25-39: metadata `GET /exams/{exam_id}`.
- 40-57: `get_exam_detail`.
- 60-74: metadata `GET /exams/{exam_id}/audit-events`.
- 75-88: `get_exam_audit_events`.
- 91-117: metadata `POST /exams/{exam_id}/state-transitions`.
- 118-153: `change_exam_state`:
  - chiama servizio;
  - converte eccezioni business in codici HTTP corretti (400/403/404/409).

---

## Core

### `backend/app/core/__init__.py`
- Riga 1: file vuoto, package marker.

### `backend/app/core/config.py`
A cosa serve: carica configurazione runtime da env.

Righe:
- 1-5: import cache e Pydantic Settings.
- 7-19: classe `Settings` con campi config (app, DB, JWT).
- 20-25: `model_config` per leggere `.env`.
- 27-42: validator `normalize_debug` (accetta varie forme stringa true/false).
- 45-47: `get_settings()` con `@lru_cache`.
- 50: `settings` singleton usato nel progetto.

### `backend/app/core/exceptions.py`
A cosa serve: eccezioni custom.

Righe:
- 1-2: eccezione base `RevelioException`.
- 5-26: eccezioni specifiche (`AuthenticationError`, `AuthorizationError`, `InvalidStateTransitionError`, ecc.).

### `backend/app/core/security.py`
A cosa serve: password hashing + token JWT.

Righe:
- 1-10: import crypto/JWT e config.
- 12: inizializza `CryptContext` con bcrypt.
- 15-16: `verify_password`.
- 19-20: `get_password_hash`.
- 23-37: `create_access_token`:
  - calcola scadenza;
  - crea payload con `sub`, `iat`, `exp`;
  - firma JWT.
- 40-49: `decode_access_token`, decode JWT e rilancia errore auth se non valido/scaduto.

### `backend/app/core/time.py`
A cosa serve: utilità tempo UTC e fusi orari.

Righe:
- 1-2: import datetime/zoneinfo.
- 5: costante timezone Roma.
- 8-9: `now_utc`.
- 12-13: `now_rome`.
- 16-20: `to_utc` valida datetime timezone-aware e converte.
- 23-27: `rome_day_bounds_utc` (inizio/fine giorno Roma convertiti in UTC).
- 30-33: `rome_shift_window_utc` (finestra turno per data e ore).

---

## DB

### `backend/app/db/__init__.py`
- Riga 1: file vuoto, package marker.

### `backend/app/db/session.py`
A cosa serve: setup SQLAlchemy.

Righe:
- 1-7: import SQLAlchemy + settings.
- 9-10: classe `Base` ORM.
- 13: `connect_args` specifico per SQLite (`check_same_thread=False`).
- 15-18: crea `engine`.
- 20-25: crea `SessionLocal` (factory sessioni DB).
- 28-33: dependency `get_db()` usata negli endpoint (yield + close sicuro).

### `backend/app/db/base.py`
A cosa serve: importa tutti i modelli così `Base.metadata` conosce tutte le tabelle.

Righe:
- 1-7: import `Base` e modelli.
- 9-17: `__all__` export.

---

## Dependencies

### `backend/app/dependencies/__init__.py`
Righe:
- 1: importa `bearer_scheme` e `get_current_technician`.
- 3-6: li esporta in `__all__`.

### `backend/app/dependencies/auth.py`
A cosa serve: risolve utente autenticato da token Bearer.

Righe:
- 1-10: import FastAPI auth, DB e servizi.
- 12: `HTTPBearer(auto_error=False)`.
- 15-54: `get_current_technician`:
  - controlla token presente;
  - decodifica JWT;
  - legge `sub` e lo converte in int;
  - carica tecnico da DB con `AuthService`;
  - mappa errori a HTTP 401/403.

---

## Models

### `backend/app/models/__init__.py`
- 1-6: import modelli.
- 8-15: export in `__all__`.

### `backend/app/models/enums.py`
- 1-2: import Enum.
- 4-7: `MachineCode` (`RM`, `TC`, `RX`).
- 10-14: `SessionStatus` (`PLANNED`, `ACTIVE`, `CLOSED`).
- 16-21: `ExamStatus` (`SCHEDULED`, `ARRIVED`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED`).

### `backend/app/models/machine.py`
A cosa serve: tabella macchine.

Righe:
- 1-13: import ORM + enum.
- 15-35: campi tabella `machines` (`id`, `code`, `display_name`, `is_active`).
- 38-41: relazione `sessions`.
- 43-44: helper `is_selectable`.
- 46-47: helper label codice.
- 49-50: `__repr__`.

### `backend/app/models/technician.py`
A cosa serve: tabella tecnici.

Righe:
- 1-15: import e type checking.
- 17-53: campi (`username`, `password_hash`, `full_name`, `is_active`, timestamp).
- 56-59: relazione `sessions`.
- 62-65: relazione `audit_events`.
- 67-68: helper `is_enabled`.
- 70-71: helper nome visualizzato.
- 73-74: `__repr__`.

### `backend/app/models/session.py`
A cosa serve: tabella turni/sessioni operative.

Righe:
- 1-17: import e type hints.
- 19-60: campi (`machine_id`, `technician_id`, `start_at`, `end_at`, `status`, timestamp).
- 63-70: relazioni macchina/tecnico.
- 73-76: relazione esami.
- 78-85: helper stato sessione (`is_active`, `is_planned`, `is_closed`).
- 87-88: `belongs_to(technician_id)`.
- 90-94: `__repr__`.

### `backend/app/models/patient.py`
A cosa serve: tabella pazienti.

Righe:
- 1-14: import base.
- 16-49: campi (`patient_code`, nome/cognome, nascita, sesso, created_at).
- 52-55: relazione esami.
- 57-61: helper full name e stringa identità.
- 63-64: helper `has_birth_date`.
- 66-67: `__repr__`.

### `backend/app/models/exam.py`
A cosa serve: tabella esami + regole FSM.

Righe:
- 1-17: import e type hints.
- 19-67: campi tabella (`exam_code`, FK session/patient, orari, stato, timestamp).
- 70-77: relazioni con sessione e paziente.
- 80-84: relazione `audit_events` ordinata per data.
- 86-95: definizione transizioni valide FSM.
- 97-101: helper transizioni consentite/can transition.
- 103-104: richiede nota solo per `CANCELLED`.
- 106-123: helper boolean per stato corrente.
- 124-125: `__repr__`.

### `backend/app/models/exam_audit_event.py`
A cosa serve: storico delle transizioni stato.

Righe:
- 1-16: import.
- 18-57: campi tabella audit (`from_status`, `to_status`, `note`, `performed_at`, `meta`).
- 60-67: relazioni verso esame e tecnico.
- 69-81: helper coerenza evento (`is_cancellation`, `has_mandatory_note`, `is_consistent`).
- 83-87: `__repr__`.

---

## Repositories

### `backend/app/repositories/__init__.py`
- 1-5: importa repository.
- 7-13: export in `__all__`.

### `backend/app/repositories/technician_repository.py`
A cosa serve: query base tecnici.

Righe:
- 1-5: import.
- 7-13: `get_by_id`.
- 15-19: `get_by_username`.
- 21-25: `list_all` ordinato per username.

### `backend/app/repositories/machine_repository.py`
A cosa serve: query macchine.

Righe:
- 1-6: import.
- 10-14: `get_by_id`.
- 16-20: `get_by_code`.
- 22-24: `list_all`.
- 26-32: `list_active` (`is_active=True`).

### `backend/app/repositories/session_repository.py`
A cosa serve: query sessioni con logica finestra giorno/turno.

Righe:
- 1-10: import.
- 14-17: `_get_relevant_window_start` (inizio giorno Roma in UTC).
- 19-29: `get_by_id` con join machine+technician.
- 30-47: `list_by_machine_id` (solo sessioni rilevanti nel giorno).
- 48-66: `list_by_machine_code`.
- 67-96: `get_active_for_machine` (stato ACTIVE e finestra oraria valida).
- 97-125: `get_active_for_technician`.
- 127-142: `list_by_technician_id`.

### `backend/app/repositories/exam_repository.py`
A cosa serve: query esami e update stato.

Righe:
- 1-13: import.
- 17-27: `get_by_id` con eager loading relazioni.
- 29-40: `get_by_id_with_audit` include audit + autore evento.
- 42-54: `list_by_session_id` ordinata per orario.
- 55-70: `list_by_session_ids`.
- 71-84: `list_by_machine_id`.
- 85-101: `update_state` aggiorna `status`, `status_updated_at`, `updated_at`.
- 103-106: `save` generico.

### `backend/app/repositories/audit_repository.py`
A cosa serve: creazione e lettura audit eventi.

Righe:
- 1-10: import.
- 14-39: `create` evento audit.
- 41-47: `get_by_id` con join tecnico autore.
- 49-56: `list_by_exam_id` ordinata cronologicamente.

---

## Schemas

### `backend/app/schemas/__init__.py`
A cosa serve: export centralizzato di tutti gli schemi Pydantic.

Righe:
- 1-34: import schemi da file diversi.
- 35-61: elenco `__all__`.

### `backend/app/schemas/common.py`
Righe:
- 1: import base Pydantic.
- 4-7: `ORMBaseSchema` con `from_attributes=True`.
- 9-12: `MessageResponse`.
- 14-16: `ErrorResponse`.

### `backend/app/schemas/auth.py`
Righe:
- 1-4: import.
- 6-22: `LoginRequest` (username/password validati).
- 24-35: `TokenResponse`.
- 37-43: `AuthenticatedTechnicianResponse`.
- 45-58: `LoginResponse` (token + tecnico).

### `backend/app/schemas/audit.py`
Righe:
- 1-8: import.
- 10-15: `AuditPerformedByResponse`.
- 17-39: `AuditEventResponse` base.
- 41-62: `AuditEventDetailedResponse` con campo nested `performed_by`.

### `backend/app/schemas/session.py`
Righe:
- 1-7: import.
- 9-13: `SessionTechnicianInfo`.
- 15-20: `SessionMachineInfo`.
- 22-37: `SessionSummaryResponse`.
- 39-50: `SessionListItemResponse`.

### `backend/app/schemas/machine.py`
Righe:
- 1-7: import.
- 9-15: `MachineResponse`.
- 17-23: `WorklistPatientResponse`.
- 25-39: `WorklistExamResponse`.
- 41-57: `WorklistSessionResponse`.
- 59-76: `MachineWorklistResponse`.

### `backend/app/schemas/exam.py`
Righe:
- 1-8: import.
- 10-24: `ExamPatientResponse`.
- 26-31: `ExamMachineResponse`.
- 33-45: `ExamSessionResponse`.
- 47-76: `ExamDetailResponse`.
- 78-99: `ExamStateTransitionRequest` + validator `normalize_note`.
- 101-128: `ExamStateTransitionResponse`.

---

## Seed

### `backend/app/seed/__init__.py`
Righe:
- 1-5: importa costanti login e funzione seed.
- 7-11: export in `__all__`.

### `backend/app/seed/seed_data.py`
A cosa serve: crea dataset coerente con turni reali e regole FSM.

Righe (principali):
- 1-18: import.
- 20-23: costanti credenziali login demo default.
- 24-46: definizione tecnici demo (full name, username, password, legacy username).
- 48-52: mappa macchina -> username tecnico assegnato.
- 54-160: anagrafica pazienti demo.
- 162-217: blueprint turni per macchina (`AM`/`PM`) con 5 esami e stati target.
- 220-236: `seed_database` orchestratore con commit/rollback.
- 238-266: `_seed_technicians` upsert tecnici + hash password.
- 268-306: `_seed_machines` upsert macchine.
- 308-333: `_seed_patients` upsert pazienti.
- 335-339: normalizzazione data nascita.
- 342-403: `_seed_sessions`:
  - calcola finestra oraria del giorno corrente;
  - determina stato sessione (planned/active/closed);
  - aggiorna/ricrea sessioni vecchie.
- 405-416: `_resolve_session_status`.
- 418-471: `_seed_exams_and_audit`:
  - se sessione NON attiva imposta tutti esami a `SCHEDULED`;
  - se attiva usa stati blueprint;
  - aggiorna catena audit coerente.
- 473-543: `_build_audit_events` costruisce storicizzazione in base allo stato finale.
- 545-568: `_replace_audit_chain_for_exam` reset + insert eventi audit.
- 570-627: helper query interne (`_get_*`, `_list_sessions_by_machine`, `_delete_session_tree`).

Nota importante backend/frontend:
- La regola "fuori fascia oraria -> esami `SCHEDULED`" è implementata qui in seed.
- La regola "solo tecnico assegnato e durante fascia può cambiare FSM" è applicata nel servizio `exam_state_service.py`.

---

## Services

### `backend/app/services/__init__.py`
Righe:
- 1-2: importa `AuthService` e `WorklistService`.
- 4-7: export in `__all__`.

### `backend/app/services/auth_service.py`
A cosa serve: autentica tecnico e recupera tecnico corrente.

Righe:
- 1-7: import.
- 9-13: init repository.
- 14-29: `authenticate`:
  - cerca utente;
  - verifica password;
  - verifica account attivo;
  - genera JWT.
- 31-39: `get_current_technician` con controlli esistenza/attivo.

### `backend/app/services/worklist_service.py`
A cosa serve: costruisce payload worklist macchina già pronto per frontend.

Righe:
- 1-20: import.
- 22-28: init repository.
- 29-32: `list_machines`.
- 33-97: `get_machine_worklist`:
  - valida macchina;
  - legge sessioni e sessione attiva;
  - legge esami;
  - raggruppa per sessione;
  - costruisce risposta strutturata con `is_active_now`.

### `backend/app/services/exam_state_service.py`
A cosa serve: regole business su dettagli esame e transizioni FSM.

Righe:
- 1-28: import.
- 30-35: init repository esami/audit.
- 36-51: `get_exam_detail`.
- 52-66: `list_audit_events`.
- 67-135: `request_state_change`:
  - carica esame;
  - controlla autorizzazione (tecnico + finestra oraria);
  - valida transizione e nota cancellazione;
  - aggiorna stato;
  - crea audit;
  - commit/rollback;
  - ritorna response completa.
- 136-146: `_check_authorization` (vincolo tecnico assegnato + turno attivo).
- 147-150: `_validate_transition`.
- 151-158: `_validate_mandatory_note`.
- 159-203: `_build_exam_detail_response`:
  - se non autorizzato o fuori turno, `allowed_transitions` diventa lista vuota.
- 205-210: utility datetime UTC aware.
- 212-220: `_is_within_session_window`.
- 222-236: `_build_audit_event_response`.

---

## Script

### `backend/scripts/smoke_test.py`
A cosa serve: test automatico "fumo" end-to-end (backend + frontend + regole principali).

Righe:
- 1-23: import e costanti test.
- 25-47: `main`:
  - crea DB temporaneo;
  - avvia server su porta libera;
  - esegue controlli;
  - chiude server e rimuove DB temp.
- 49-245: `run_checks`:
  - verifica pagine frontend;
  - verifica `/health`;
  - login;
  - fetch macchine/worklist;
  - controlla coerenza slot turni;
  - controlla regole FSM (solo tecnico autorizzato / fuori turno bloccato / nota CANCELLED obbligatoria / audit persistito).
- 246-280: helper `fetch` HTTP.
- 282-302: `start_server` (subprocess uvicorn).
- 305-325: `wait_for_health`.
- 327-337: `stop_server`.
- 339-342: `find_free_port`.
- 345-350: parsing datetime API.
- 353-357: helper assert `check`.
- 360-361: entrypoint script.

---

## Frontend

### `frontend/index.html`
A cosa serve: pagina shell minima; il rendering reale lo fa `app.js`.

Righe:
- 1-3: doctype e lingua italiana.
- 4-13: meta tag base (charset, viewport, descrizione).
- 14-19: preload font Google.
- 20-22: preload immagini macchine.
- 23: favicon da `/images/favicon.svg`.
- 24: include stylesheet.
- 27: contenitore root `<div id="app">`.
- 28-30: definisce base API globale (`window.REVELIO_API_BASE`).
- 31: carica modulo `app.js`.

### `frontend/app.js`
A cosa serve: gestisce tutto il comportamento client (state, eventi, render, API, refresh).

Spiegazione riga-per-riga per blocchi/funzioni:
- 1-24: costanti API, timezone, credenziali demo, mapping immagini macchine.
- 26-52: configurazione etichette/classi per stati FSM.
- 54-59: configurazione bottoni azione transizioni.
- 61-73: etichette stato sessione e linee workflow.
- 75-99: stato globale applicazione (`state`).
- 100-106: variabili timer/supporto refresh/scroll.
- 108-118: event listeners globali (`click`, `submit`, `input`, `scroll`, `resize`, `focus`, `visibilitychange`).
- 120: bootstrap iniziale.

Funzioni principali:
- 122-145 `boot()`: ripristina sessione da `sessionStorage`, valida token e carica dashboard.
- 147-233 `handleClick()`: dispatcher azioni UI (`logout`, `open-machine`, `open-exam`, transizioni, ecc.).
- 235-248 `handleSubmit()`: login form e form nota cancellazione.
- 250-267 `handleInput()`: aggiorna stato campi form.
- 269-303 `login()`: login API, salva token/utente, carica dashboard.
- 305-339 `loadDashboard()`: carica macchine + worklist aggregate.
- 341-358 `openMachine()`: apre worklist macchina.
- 360-378 `openExam()`: apre dettaglio esame.
- 380-388 `refreshMachineWorklist()`: refresh worklist selezionata.
- 390-397 `refreshExamDetail()`: refresh dettaglio esame.
- 399-444 `changeExamStatus()`: invia transizione FSM, valida nota cancellazione, refresh dati.
- 446-482 `apiFetch()`: wrapper `fetch` con token Bearer, parse JSON, gestione errori e session expiry.
- 484-500 `render()`: rendering root + sync chrome scrollbar/top bar.
- 502-520 `renderScreen()`: mini router UI (`loading`, `login`, `home`, `worklist`, `examDetail`).

Gestione refresh/scrollbar:
- 522-532 `handlePageScroll()`.
- 534-569 `syncPageChrome()`.
- 571-577 `queueChromeSync()`.
- 579-581 `isScrollableView()`.
- 583-591 `showScrollbarTemporarily()`.
- 593-598 `hasPageVerticalOverflow()`.
- 600-612 `resetScrollbarTimer()` + `clearScrollbarTimer()`.

Render template UI:
- 614-636 `renderToast()`.
- 638-651 `renderLoading()`.
- 653-709 `renderLogin()`.
- 711-724 `renderDemoUser()`.
- 726-769 `renderHome()` dashboard.
- 771-779 `renderDashboardSkeleton()`.
- 781-831 `renderMachineCard()`.
- 833-952 `renderWorklist()`.
- 954-972 `renderWorklistSkeleton()`.
- 974-1002 `renderExamRow()` (allineamento colonne e bordo verde solo `IN_PROGRESS`).
- 1004-1032 `collectSessionsOverview()`.
- 1034-1057 `renderSessionOverviewItem()`.
- 1059-1187 `renderExamDetail()`.
- 1189-1202 `renderExamSkeleton()`.
- 1204-1222 `renderTopBar()`.
- 1224-1231 `renderInfoBlock()`.
- 1233-1266 `renderActionButton()`.
- 1268-1286 `renderAuditItem()`.
- 1288-1299 `renderStatusBadge()`.
- 1301-1312 `renderMachineArtwork()`.

Utility dati/tempo/business lato client:
- 1314-1327 `flattenExams()`.
- 1329-1337 `normalizedSessions()`.
- 1339-1350 `findMachineActiveSession()`.
- 1352-1383 `findDashboardReferenceShift()`.
- 1385-1405 `countMachinesInShift()` (conta macchine davvero attive nel turno mostrato).
- 1407-1435 `triggerAutoRefresh()`.
- 1437-1446 `isSessionInProgress()`.
- 1448-1452 `findUpcomingMachineSession()`.
- 1454-1460 label status/session.
- 1462-1497 formatter data/ora.
- 1499-1515 `getGreeting()`.
- 1517-1530 toast show/clear.
- 1532-1549 `clearSession()`.
- 1551-1563 `toDate()` parser robusto date ISO.
- 1565-1575 `parseJson()` sicuro.
- 1577-1584 `escapeHtml()` anti-injection nel render template literal.

### `frontend/styles.css`
A cosa serve: stile completo app (design tokens, layout, tabella, topbar, responsive, animazioni).

Spiegazione riga-per-riga per blocchi:
- 1-62: variabili CSS globali (font, colori, spacing, raggi, ombre, colonne tabella).
- 64-139: reset base (`box-sizing`, body, scrollbar, elementi base).
- 141-173: wrapper app/screen e gestione viewport worklist.
- 174-247: utility shell e stile toast.
- 249-327: loading screen/card/animazione.
- 328-408: layout e parte visuale login (gradient blu/bianco).
- 410-487: pannello login + form controls.
- 489-514: box messaggi (`error`, `warning`, `info`).
- 516-570: bottoni base (`primary`, `secondary`, `ghost`, `action`).
- 572-627: blocco credenziali demo login.
- 629-720: top bar (logo, greeting, logout) + copertura gap scrollbar.
- 722-778: layout pagina, titoli, testi giustificati dashboard/worklist.
- 780-817: hero chip (numero macchine attive e testo inline).
- 818-960: card macchine, badge stati, visual immagini.
- 962-999: griglia layout pannelli e header panel.
- 1000-1037: summary cards worklist.
- 1038-1149: tabella worklist:
  - colonne allineate al centro;
  - badge stato centrati;
  - bordo verde solo righe `IN_PROGRESS`.
- 1150-1207: stack sessioni operative.
- 1209-1299: layout dettaglio esame e info blocks.
- 1301-1335: varianti colore bottoni FSM.
- 1337-1407: nota inline, audit list, workflow box.
- 1409-1493: link back, empty state, skeleton, keyframes.
- 1495-1603: media query responsive desktop/tablet/mobile.

### `frontend/images/*`
- `favicon.svg`: icona tab browser.
- `Risonanza magnetica.jpg`: asset visuale macchina RM.
- `Tomografia computerizzata.png`: asset visuale macchina TC.
- `Radiografia.png`: asset visuale macchina RX.

Questi file sono binari/immagini: non hanno codice riga-per-riga.

---

## 4) Flusso completo backend <-> frontend (in parole semplici)

1. Apri il browser su `/`.
2. `index.html` carica `app.js` + `styles.css`.
3. Login invia `POST /api/v1/auth/login`.
4. Backend verifica password hash, genera JWT e risponde.
5. Frontend salva token in `sessionStorage`.
6. Dashboard chiama `/machines` e `/machines/{code}/worklist`.
7. Worklist mostra esami ordinati per orario.
8. Dettaglio esame chiama `/exams/{id}`.
9. Se tecnico autorizzato e in fascia oraria, frontend riceve `allowed_transitions`.
10. Cambio stato manda `POST /exams/{id}/state-transitions`.
11. Backend valida FSM, salva stato, crea evento audit.
12. Frontend aggiorna worklist + dettaglio in tempo reale.

---

## 5) Punti che devi sapere per spiegare il progetto al professore

- Frontend: JavaScript vanilla (non React/Vue/Angular).
- Backend: FastAPI + SQLAlchemy + Pydantic.
- DB: SQLite locale (`revelio.db`).
- Auth: JWT Bearer token.
- FSM esami: `SCHEDULED -> ARRIVED -> IN_PROGRESS -> COMPLETED` (con ramo `CANCELLED` secondo regole).
- Regola sicurezza importante: solo tecnico assegnato e solo nella fascia oraria può cambiare stato.
- Seed intelligente: fuori turno gli esami sono riportati a `SCHEDULED`.

---

## 6) Cosa non pubblicare su GitHub

Da NON pubblicare:
- `backend/.env`
- `backend/.venv/`
- `backend/revelio.db`
- cache (`__pycache__`, `*.pyc`)

Da pubblicare:
- codice backend/frontend
- `backend/requirements.txt`
- `backend/.env.example`
- `.gitignore`
- `README.md`
- questa guida (se vuoi consegnare documentazione completa)

