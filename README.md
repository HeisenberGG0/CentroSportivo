#  Centro Sportivo - Sistema Informativo 

Un'applicazione web sviluppata in **Django** che sostituisce le procedure manuali con un sistema digitale completo per la gestione di prenotazioni, eventi e personale di un centro sportivo.


##  Obiettivi del Progetto

Il sistema è stato progettato per rispondere alle seguenti esigenze:

- **Modernizzazione**: Sostituzione delle procedure manuali con un sistema digitale
- **Gestione Centralizzata**: Database SQL unificato per tutte le operazioni
- **Multi-Utente**: Accesso differenziato per clienti e staff
- **Efficienza**: Gestione automatizzata di prenotazioni ed eventi

---

## Caratteristiche Principali

###  **Gestione Utenti**
- Registrazione e autenticazione differenziata (Clienti/Staff)
- Profili personalizzati con storico prenotazioni
- Sistema di ruoli e privilegi

### **Gestione Strutture Sportive**
- Catalogo completo degli impianti (calcio, tennis, padel)
- Monitoraggio disponibilità in tempo reale
- Gestione capienza e stato delle strutture

###  **Sistema Prenotazioni**
- Prenotazione online con selezione data/orario
- Modifica e cancellazione prenotazioni
- Visualizzazione calendario disponibilità

### **Gestione Eventi**
- Creazione e pubblicazione eventi sportivi
- Sistema di iscrizione partecipanti
- Gestione tornei e lezioni di gruppo

### **Amministrazione Staff**
- Gestione membri del personale
- Definizione ruoli e competenze
- Struttura organizzativa del centro

---

##  Tecnologie Utilizzate

| Componente | Tecnologia |
|------------|------------|
| **Backend** | [Django] Python 3.13 |
| **Database** | [SQLite]|
| **Frontend** | [Bootstrap]+ Django Templates |
| **Styling** | [CSS3] Bootstrap CSS |

---

##  Requisiti di Sistema

- **Python**: 3.13 o superiore
- **Django**: Framework web Python
- **SQLite**: Database (incluso di default)
- **Browser**: Qualsiasi browser 

---

##  Installazione e Configurazione

### **1. Clona il Repository**

```bash
git clone https://github.com/HeisenberGG0/CentroSportivo.git
cd CentroSportivo
```

###  **2. Installa le Dipendenze**

```bash
pip install django
```

### **3. Configura il Database**

```bash
python manage.py makemigrations
python manage.py migrate
```

###  **4. Carica i Dati di Prova** *Raccomandato*

Il progetto include un file `dump.sql` con dati di esempio completi:

```bash
sqlite3 db.sqlite3 < dump.sql
```

>  **Dati inclusi**: Utenti di test, strutture sportive, eventi di esempio, prenotazioni campione

###  **5. Crea Superuser** *(Opzionale)*

```bash
python manage.py createsuperuser
```

---

##  Avvio del Sistema

###  **Avvia il Server**

```bash
python manage.py runserver
```

###  **Accesso alle Interfacce**

| Interfaccia | URL | Descrizione |
|-------------|-----|-------------|
|  **Homepage** | http://127.0.0.1:8000/ | Interfaccia principale |
|  **Admin Panel** | http://127.0.0.1:8000/admin/ | Pannello amministrativo |

---

##  Struttura del Progetto

```
CentroSportivo/
├── manage.py                 # Script di gestione Django
├──  dump.sql                 # Dati di prova completi
├──  db.sqlite3               # Database SQLite
├──  CentroSportivo/          # Configurazione progetto
│   ├── settings.py         # Configurazioni sistema
│   ├──  urls.py             # Routing principale
│   ├──  wsgi.py & asgi.py   # Server configuration
│   └──  __init__.py
└── centro_sportivo_app/     # App principale
    ├──  migrations/          # Migrazioni database
    ├──  templates/          # Template HTML
    ├──  admin.py           # Configurazione admin
    ├──  forms.py            # Form di input
    ├──  models.py           # Modelli database
    ├──  views.py            # Logica applicazione
    └──  urls.py             # URL app
```

---

##  Guida all'Utilizzo

###  **Per i Clienti**

1. **Registrazione/Login** → Crea account o accedi
2. **Esplora Strutture** → Visualizza campi disponibili  
3. **Prenota** → Seleziona data, orario e struttura
4. **Gestisci** → Modifica o cancella prenotazioni
5. **Eventi** → Iscriviti a tornei e corsi

###  **Per lo Staff**

1. **Dashboard Staff** → Accesso con credenziali personale
2. **Gestione Prenotazioni** → Monitora e gestisce prenotazioni
3. **Creazione Eventi** → Organizza tornei e attività
4. **Amministrazione** → Gestisce strutture e utenti

---

##  Dati di Prova Inclusi

Il file `dump.sql` contiene un dataset completo per il testing:

| Categoria | Contenuto |
|-----------|-----------|
|  **Utenti** | Account clienti e staff preconfigurati |
|  **Strutture** | Campi da calcio, tennis, padel, palestre |
|  **Eventi** | Tornei, corsi e attività sportive |
|  **Prenotazioni** | Esempi di prenotazioni in vari stati |


---

##  Funzionalità Implementate

 **Registrazione e autenticazione utenti differenziata**  
 **Gestione completa delle prenotazioni**  
 **Sistema eventi con iscrizioni**  
 **Visualizzazione e ricerca disponibilità**  
 **Gestione personale e struttura organizzativa**  
 **Modifica e cancellazione prenotazioni/eventi**  

---

##  Modello Informativo

Il sistema è basato su un **modello Entità-Relazione** che include:

- **Entità principali**: Clienti, Impianti, Prenotazioni, Eventi, Staff
- **Relazioni**: Gestione delle associazioni tra entità
- **Vincoli**: Integrità referenziale e regole business
- **Specializzazioni**: Differenziazione ruoli utente

---

## Sviluppo e Consegna

> **Progetto Accademico** sviluppato secondo le specifiche della traccia d'esame


**Sviluppato per il corso di Basi di Dati - Anno Accademico 24/25**


