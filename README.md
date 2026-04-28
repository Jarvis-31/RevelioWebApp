# 🩻 Revelio Web App

Web app full-stack API-based per la gestione del workflow degli esami in una struttura sanitaria di diagnostica per immagini.

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/fastapi-0.135.3-green.svg)
![SQLite](https://img.shields.io/badge/database-SQLite-lightgrey.svg)
![Postman](https://img.shields.io/badge/test-Postman-orange.svg)

## 🚀 Avvio Rapido

Dopo aver clonato il repository, dalla cartella principale del progetto è possibile avviare l'applicazione con uno script dedicato.

### macOS / Linux

```bash
./start.sh
```
### Windows

```bat
start.bat
```

Gli script creano l'ambiente virtuale, installano le dipendenze, preparano il file `.env` locale se mancante e avviano il server FastAPI.

Accedi all'applicazione su: http://127.0.0.1:8000/

Documentazione API Swagger: http://127.0.0.1:8000/docs

## 🔐 Credenziali Demo

- Username: `Amaggio` / Password: `Alessiom92!` - Risonanza Magnetica
- Username: `Rmaselli` / Password: `Robertom79!` - Tomografia Computerizzata
- Username: `Edipiero` / Password: `Erikad98!` - Radiologia Tradizionale

## ✨ Funzionalità Principali

- 👤 Login del tecnico radiologo con autenticazione JWT
- 🖥️ Dashboard con panoramica dei macchinari disponibili
- 📋 Worklist organizzata per RM, TC e RX
- 🕒 Visualizzazione di sessioni operative e fasce orarie
- 🧑‍⚕️ Dettaglio dell'esame con dati paziente, tecnico e stato corrente
- 🔄 Cambio stato dell'esame tramite FSM
- ⛔ Blocco delle transizioni non valide o non autorizzate
- 📝 Nota obbligatoria in caso di cancellazione
- 🧾 Registrazione dello storico tramite audit event
- 📱 Frontend semplice e responsive

## 📋 Requisiti

- Python 3.11 o superiore
- Browser web aggiornato
- Accesso Internet per scaricare le dipendenze pip, se necessario
- Ambiente virtuale Python consigliato
- Sistema operativo macOS, Linux o Windows

## ⚙️ Installazione Manuale

Se si preferisce avviare il progetto senza script, seguire questi passaggi.

1. **Entra nella cartella backend**

   ```bash
   cd backend
   ```

2. **Crea e attiva l'ambiente virtuale**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

   Su Windows:

   ```bat
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Installa le dipendenze**

   ```bash
   pip install -r requirements.txt
   ```

4. **Crea il file di configurazione locale**

   ```bash
   cp .env.example .env
   ```

   Su Windows:

   ```bat
   copy .env.example .env
   ```

5. **Avvia il server**

   ```bash
   uvicorn app.main:app --reload
   ```

## 🧪 Test API con Postman

Il progetto include una collection Postman per verificare il comportamento delle API principali.

File da importare:

- `Test Postman/Revelio_API_FSM.postman_collection.json`
- `Test Postman/Revelio_Local.postman_environment.json`

Per eseguire i test:

1. Avvia il backend.
2. Importa collection ed environment in Postman.
3. Seleziona l'environment `Revelio Local`.
4. Esegui la collection completa nell'ordine previsto.

La collection verifica:

- health check dell'API
- login del tecnico radiologo
- lettura del profilo autenticato
- elenco dei macchinari
- worklist per RM, TC e RX
- dettaglio esame
- regole della FSM
- vincoli di autorizzazione
- controllo della fascia oraria
- persistenza dello stato e degli audit event
- casi di errore principali: `400`, `403`, `409`

## 🔄 Reset Database

Il progetto utilizza un database SQLite locale. Per ripristinare lo scenario dimostrativo è sufficiente eliminare:

```bash
backend/revelio.db
```

Al successivo avvio, il backend ricrea automaticamente lo schema e inserisce i dati seed.

Il seed iniziale comprende:

- 3 tecnici radiologi
- 3 macchinari: RM, TC, RX
- 15 pazienti dimostrativi
- sessioni operative giornaliere
- esami distribuiti nei diversi stati della FSM
- eventi audit iniziali per gli esami già avanzati nel workflow

## 📝 Nota

Revelio Web App è stato sviluppato come elaborato dimostrativo. L'applicazione simula il workflow radiologico e permette di verificare login, worklist, cambio stato, autorizzazioni e audit, ma non integra sistemi sanitari reali come RIS, PACS o DICOM.

Per un utilizzo reale sarebbero necessari ulteriori sviluppi su sicurezza, gestione utenti, database, backup, ruoli applicativi e integrazione con sistemi clinici.
