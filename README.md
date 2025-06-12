# Centro Sportivo - Sistema di Gestione Prenotazioni

Un sistema web sviluppato in Django per la gestione di un centro sportivo, che permette ai clienti di registrarsi, effettuare il login e prenotare strutture sportive ed eventi. Il sistema include anche un'interfaccia per il personale per gestire prenotazioni ed eventi.

## Caratteristiche

- **Gestione Utenti**: Registrazione e autenticazione per clienti e personale
- **Prenotazione Strutture**: Sistema di prenotazione per le strutture sportive disponibili
- **Gestione Eventi**: Creazione e gestione di eventi sportivi
- **Pannello Amministrativo**: Interfaccia per il personale per gestire prenotazioni ed eventi
- **Dashboard Utenti**: Area personale per visualizzare e gestire le proprie prenotazioni

## Requisiti di Sistema

- **Python**: 3.13 o superiore
- **Django**: Framework web Python
- **SQLite**: Database (incluso di default con Python)

## Installazione

### 1. Clona il Repository

```bash
git clone https://github.com/HeisenberGG0/CentroSportivo.git
cd CentroSportivo
```

### 2. Installa Django

Se non hai Django installato, esegui:

```bash
pip install django
```

### 3. Configurazione del Database

Esegui le migrazioni per configurare il database SQLite:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Carica i Dati di Prova (Raccomandato)

Il progetto include un file `dump.sql` con dati di esempio (utenti, strutture, eventi e prenotazioni). Per caricare questi dati:

```bash
sqlite3 db.sqlite3 < dump.sql
```

### 5. Crea un Superuser (Opzionale)

Se vuoi creare un nuovo superuser oltre a quelli presenti nei dati di prova:

```bash
python manage.py createsuperuser
```

Segui le istruzioni per inserire username, email e password.

## Avvio del Progetto

### Avvia il Server di Sviluppo

```bash
python manage.py runserver
```

Il server sarà disponibile all'indirizzo: **http://127.0.0.1:8000/**

### Accesso al Sistema

- **Homepage**: http://127.0.0.1:8000/
- **Pannello Admin Django**: http://127.0.0.1:8000/admin/ (usa le credenziali del superuser)

## Struttura del Progetto

```
CentroSportivo/
├── manage.py                 # Script di gestione Django
├── dump.sql                 # Dati di prova (utenti, strutture, eventi)
├── db.sqlite3               # Database SQLite (generato dopo le migrazioni)
├── CentroSportivo/          # Cartella principale del progetto
│   ├── __init__.py
│   ├── asgi.py             # Configurazione ASGI
│   ├── settings.py         # Configurazioni del progetto
│   ├── urls.py             # URL principali del progetto
│   └── wsgi.py             # Configurazione WSGI
└── centro_sportivo_app/     # App principale
    ├── migrations/         # File di migrazione del database
    ├── templates/          # Template HTML
    ├── __init__.py
    ├── admin.py           # Configurazione pannello admin
    ├── apps.py            # Configurazione app
    ├── forms.py           # Form per l'input utente
    ├── models.py          # Modelli del database
    ├── tests.py           # Test dell'applicazione
    ├── urls.py            # URL dell'app
    └── views.py           # Viste dell'applicazione
```

### Utilizzo dei Dati di Prova

Il file `dump.sql` contiene dati di esempio per testare rapidamente il sistema:

- **Utenti Cliente**: Account già registrati per testare le prenotazioni
- **Utenti Personale**: Account staff per testare la gestione
- **Strutture Sportive**: Campi da calcio, tennis, basket,pallavolo 
- **Eventi**: Tornei e corsi già configurati
- **Prenotazioni**: Esempi di prenotazioni attive

**Nota**: Controlla i dati di prova nel pannello admin per vedere username e password degli utenti di test.

## Utilizzo

### Per i Clienti
1. Registrati o effettua il login
2. Naviga tra le strutture disponibili
3. Prenota le strutture sportive desiderate
4. Visualizza gli eventi disponibili e partecipa

### Per il Personale
1. Accedi con le credenziali del personale
2. Gestisci le prenotazioni dei clienti
3. Crea e modifica eventi sportivi



## Tecnologie Utilizzate

- **Backend**: Django (Python 3.13)
- **Database**: SQLite3
- **Frontend**: HTML Templates Django


## Contributi

Per contribuire al progetto:
1. Fai un fork del repository
2. Crea un branch per la tua feature
3. Commit le modifiche
4. Apri una Pull Request

## Licenza

Questo progetto è sviluppato per scopi educativi/accademici.

---

**Sviluppato con Django Framework**
