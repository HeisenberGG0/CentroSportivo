---Traccia d’Esame – Progetto di Sistema Informativo per Centro Sportivo---	

Il progetto prevede la realizzazione di un sistema informativo completo per modernizzare la gestione di un centro sportivo, sostituendo le attuali procedure manuali con un'applicazione web intuitiva ed efficiente. Il cuore del sistema sarà un database SQL che conterrà tutte le informazioni necessarie per organizzare in modo efficace le prenotazioni, la gestione delle risorse e il profilo degli utenti.

Il database includerà i dettagli di tutti gli impianti sportivi presenti nel centro, come campi da calcio, tennis, e padel. Per ogni impianto verranno memorizzate informazioni come la tipologia del campo, la disponibilità oraria, la capienza massima e lo stato attuale. Sarà possibile visualizzare rapidamente la disponibilità di ciascun campo in base alla data e all’orario.

Gli utenti del sistema saranno principalmente suddivisi tra clienti privati e staff del centro sportivo, con ruoli e privilegi differenziati. Per i clienti verranno registrati dati come nome, contatto e storico prenotazioni; per lo staff invece saranno rilevanti ruoli (ad esempio: responsabile prenotazioni, manutenzione), orari di servizio e ambito di competenza. L’accesso al sistema sarà regolato da credenziali personali.

La funzionalità principale dell'applicazione sarà la gestione delle prenotazioni, che consentirà agli utenti di riservare un campo per una determinata fascia oraria, modificare o disdire la prenotazione. 

L'applicazione includerà anche la possibilità di gestire eventi sportivi organizzati dal centro, come tornei, lezioni di gruppo, allenamenti collettivi o giornate promozionali. Il sistema permetterà la pubblicazione delle informazioni sull’evento e l’iscrizione dei partecipanti.

Infine, sarà presente una sezione dedicata alla gestione del personale, in cui saranno registrati i membri dello staff, le loro mansioni e i rapporti gerarchici. Questa sezione faciliterà l’organizzazione interna e offrirà un riferimento chiaro agli utenti che desiderano contattare il centro per informazioni o assistenza specifica.

---Obiettivi del Progetto---

1. Analisi e progettazione concettuale

A partire dalla descrizione del contesto, analizza il dominio e costruisci un modello entità-relazione completo, includendo eventuali relazioni di generalizzazione/specializzazione tra entità. Spiega in modo chiaro come hai gestito tali relazioni e motiva le scelte effettuate.

2. Progettazione logica

Deriva il modello logico relazionale dal modello E-R, includendo una descrizione scritta dei vincoli rilevanti e giustificando eventuali semplificazioni o adattamenti.

3. Implementazione del sistema informativo
   
Utilizzando Django, realizza un’applicazione che permetta la gestione dei dati modellati e l’accesso ad almeno quattro funzionalità tra quelle previste nella descrizione iniziale. Tra le funzionalità realizzabili, si possono includere:
•	Registrazione e autenticazione degli utenti (differenziati per ruolo).
•	Registrazione e gestione delle prenotazioni.
•	Visualizzazione e iscrizione agli eventi.
•	Visualizzazione e ricerca disponibilità.
• Visualizzazione del personale e della struttura organizzativa
• Eliminazione e modifica di prenotazioni
• Modifiche e cancellazione di eventi

L’applicazione deve essere realizzata utilizzando esclusivamente:

•	Backend Django

•	Sistema di template di Django per la generazione delle pagine

•	Bootstrap CSS per la parte grafica

L’uso di JavaScript è da limitare ai soli casi in cui sia indispensabile.

---Consegna---

Il progetto deve essere caricato su un repository GitHub privato. Il link al repository va condiviso via e-mail con il docente almeno 7 giorni prima della data dell’esame.
Il repository deve contenere:

•	Documentazione con il modello informativo e le scelte progettuali.

•	Codice sorgente completo e funzionante.

•	Dati di esempio sufficienti per mostrare il funzionamento del sistema (dump del database).

•	Istruzioni per installazione e avvio del progetto.


---Bonus (facoltativo)---

È possibile includere una simulazione di attacco al sistema, ad esempio:

•	SQL injection

•	attacco a dizionario

•	attacco brute-force

Lo scopo è mostrare come vulnerabilità comuni possono essere sfruttate e come è possibile prevenirle con misure appropriate.


