# Test API con Postman (Revelio)

## File inclusi
- `Revelio_API_Smoke_FSM.postman_collection.json`
- `Revelio_Local.postman_environment.json`

## Cosa verifica la collection
- Health check API.
- Login tecnico e lettura profilo (`/auth/me`).
- Elenco macchine attive.
- Worklist per RM, TC, RX.
- Regola seed sessioni:
  - sessione attiva -> copertura FSM completa (`SCHEDULED, ARRIVED, IN_PROGRESS, COMPLETED, CANCELLED`)
  - sessione non attiva -> tutti gli esami `SCHEDULED`
- Sicurezza/autorizzazioni:
  - esame non assegnato al tecnico -> transizioni FSM vietate (`403`)
  - esame assegnato ma fuori fascia oraria -> transizioni FSM vietate (`403`)
- Caso positivo su esame assegnato in fascia attiva:
  - transizione consentita (`200`)
  - persistenza stato e audit event
- Copertura UC-06 (errori da sequence diagram):
  - `CANCELLED` senza nota -> `400`
  - errore autorizzazione -> `403`
  - errore transizione non valida -> `409`

Mappatura diretta ai diagrammi:
- `19_Sequence diagram - UC-06 - CANCELLED senza nota (400).pdf` -> request `22. UC-06 - CANCELLED senza nota (400)`
- `20_Sequence diagram - UC-06 - Errore autorizzazione (403).pdf` -> request `23. UC-06 - Errore autorizzazione (403)`
- `21_Sequence diagram - UC-06 - Errore transizione non valida (409).pdf` -> request `24. UC-06 - Errore transizione non valida (409)`

## Come eseguire in Postman
1. Avvia il backend:
   - `cd backend`
   - `source .venv/bin/activate`
   - `uvicorn app.main:app --reload`
2. Importa in Postman i due file (collection + environment).
3. Seleziona environment `Revelio Local`.
4. Esegui la collection intera con Collection Runner (ordine già numerato 01..14).
5. La sezione UC dedicata è nei request `15..25`.

## Credenziali di default
- Username: `Amaggio`
- Password: `Alessiom92!`

Puoi cambiarle dall'environment Postman senza modificare il codice.

## Esecuzione da terminale con Newman (opzionale)
Se vuoi esecuzione CLI:
1. Installa Newman:
   - `npm install -g newman`
2. Esegui:
   - `newman run backend/tests/postman/Revelio_API_Smoke_FSM.postman_collection.json -e backend/tests/postman/Revelio_Local.postman_environment.json`
