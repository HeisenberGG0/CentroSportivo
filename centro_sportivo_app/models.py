from django.db import models

# Create your models here.
# gestione_centro/models.py
from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.core.validators import RegexValidator
from django.utils import timezone


class Cliente(models.Model):
    username = models.CharField(max_length=15, unique=True)
    nome = models.CharField(max_length=20)
    cognome = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=15, blank=True)
    password = models.CharField(max_length=128)  # Password hashata
    is_active = models.BooleanField(default=True)
    codice_fiscale = models.CharField(
        max_length=16,
        blank=True,
        validators=[RegexValidator(r'^[A-Z0-9]{16}$', 'Inserisci un codice fiscale valido')]
    )

    # Campi automatici per tracciare registrazione
    data_registrazione = models.DateTimeField(auto_now_add=True)
    ultimo_accesso = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clienti"

    def __str__(self):
        return f"{self.nome} {self.cognome} ({self.username})"

    def set_password(self, raw_password):
        """Imposta la password hashata"""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Verifica la password"""
        return check_password(raw_password, self.password)

    def get_full_name(self):
        """Restituisce nome completo"""
        return f"{self.nome} {self.cognome}"


class Personale(models.Model):
    RUOLO_CHOICES = [
        ('responsabile_prenotazioni', 'Responsabile Prenotazioni'),
        ('manutenzione', 'Manutenzione'),
        ('istruttore', 'Istruttore'),
        ('manager', 'Manager'),
        ('receptionist', 'Receptionist'),
    ]

    username = models.CharField(max_length=150, unique=True)
    nome = models.CharField(max_length=30)
    cognome = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=15, blank=True)
    password = models.CharField(max_length=128)  # Password hashata
    is_active = models.BooleanField(default=True)
    ruolo = models.CharField(max_length=30, choices=RUOLO_CHOICES)
    orario_servizio = models.CharField(max_length=100)
    ambito_competenza = models.CharField(max_length=200)

    # Campi automatici per tracciare registrazione
    data_assunzione = models.DateTimeField(auto_now_add=True)
    ultimo_accesso = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Personale"
        verbose_name_plural = "Personale"

    def __str__(self):
        return f"{self.nome} {self.cognome} - {self.get_ruolo_display()}"

    def set_password(self, raw_password):
        "imposta la password hashata"
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Verifica la password"""
        return check_password(raw_password, self.password)

    def get_full_name(self):
        """Restituisce nome completo"""
        return f"{self.nome} {self.cognome}"


class Impianto(models.Model):

    TIPOLOGIA_CHOICES = [
        ('calcio', 'Campo da Calcio'),
        ('tennis', 'Campo da Tennis'),
        ('padel', 'Campo da Padel'),
        ('basket', 'Campo da Basket'),
        ('pallavolo', 'Campo da Pallavolo'),
    ]

    STATO_CHOICES = [
        ('disponibile', 'Disponibile'),
        ('prenotato', 'Prenotato'),
        ('manutenzione', 'In Manutenzione'),
        ('fuori_servizio', 'Fuori Servizio'),
    ]

    nome = models.CharField(max_length=100)
    tipologia = models.CharField(max_length=20, choices=TIPOLOGIA_CHOICES)
    capacita_massima = models.PositiveIntegerField()
    stato = models.CharField(max_length=20, choices=STATO_CHOICES, default='disponibile')
    tariffa_oraria = models.DecimalField(max_digits=6, decimal_places=2)

    # Relazione Many-to-Many con Personale attraverso GestioneImpianto
    personale_assegnato = models.ManyToManyField(
        Personale,
        through='GestioneImpianto',
        blank=True
    )

    class Meta:
        verbose_name = "Impianto"
        verbose_name_plural = "Impianti"

    def __str__(self):
        return f"{self.nome} ({self.get_tipologia_display()})"

    def is_disponibile(self, data, ora_inizio, ora_fine):
        """Verifica se l'impianto è disponibile in una fascia oraria"""
        if self.stato != 'disponibile':
            return False

        # Controlla sovrapposizioni con prenotazioni esistenti
        prenotazioni_sovrapposte = self.prenotazione_set.filter(
            data=data,
            stato__in=['Attesa']
        ).filter(
            models.Q(ora_inizio__lt=ora_fine) & models.Q(ora_fine__gt=ora_inizio)
        )

        return not prenotazioni_sovrapposte.exists()


class Prenotazione(models.Model):

    STATO_CHOICES = [
        ('attesa', 'Attesa'),
        ('annullata', 'Annullata'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    impianto = models.ForeignKey(Impianto, on_delete=models.CASCADE)
    data = models.DateField()
    ora_inizio = models.TimeField()
    ora_fine = models.TimeField()
    stato = models.CharField(max_length=15, choices=STATO_CHOICES, default='Attesa')
    importo_totale = models.DecimalField(max_digits=8, decimal_places=2)
    pagamento_effettuato = models.BooleanField(default=False)

    # Campo opzionale per il personale che gestisce la prenotazione
    gestita_da = models.ForeignKey(
        Personale,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='prenotazioni_gestite'
    )

    # Campi automatici per tracciare creazione e modifica
    data_creazione = models.DateTimeField(auto_now_add=True)
    data_modifica = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Prenotazione"
        verbose_name_plural = "Prenotazioni"
        # Evita sovrapposizioni di prenotazioni
        unique_together = ['impianto', 'data', 'ora_inizio']

    def __str__(self):
        return f"{self.cliente} - {self.impianto} - {self.data} {self.ora_inizio}"

    def durata_ore(self):
        """Calcola la durata della prenotazione in ore"""
        from datetime import datetime, timedelta
        inizio = datetime.combine(self.data, self.ora_inizio)
        fine = datetime.combine(self.data, self.ora_fine)
        durata = fine - inizio
        return durata.total_seconds() / 3600

    def calcola_importo(self):
        """"Calcola l'importo totale basato sulla durata e tariffa"""
        durata = self.durata_ore()
        return durata * float(self.impianto.tariffa_oraria)


class Evento(models.Model):
    TIPO_CHOICES = [
        ('calcio', 'Calcio'),
        ('tennis', 'Tennis'),
        ('padel', 'Padel'),
        ('basket', 'Basket'),
        ('pallavolo', 'Pallavolo'),
    ]

    organizzatore = models.ForeignKey(Personale,on_delete=models.SET_NULL, null=True, blank=True,
        related_name='eventi_organizzati',
        verbose_name="Organizzatore"
    )
    nome = models.CharField(max_length=200)
    descrizione = models.TextField()
    tipo=models.CharField(max_length=20, choices=TIPO_CHOICES,default='NULL')
    data_ora_inizio = models.DateTimeField()
    data_ora_fine = models.DateTimeField()
    posti_disponibili = models.PositiveIntegerField()
    costo_iscrizione = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    # Relazione Many-to-Many con Impianto attraverso UtilizzoImpiantoEvento
    impianti_utilizzati = models.ManyToManyField(
        Impianto,
        through='UtilizzoImpiantoEvento'
    )

    # Relazione Many-to-Many con Cliente attraverso Partecipazione
    partecipanti = models.ManyToManyField(
        Cliente,
        through='Partecipazione',
        blank=True
    )

    # Campi automatici
    data_creazione = models.DateTimeField(auto_now_add=True)
    data_modifica = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventi"
        ordering = ['data_ora_inizio']

    def __str__(self):
        return f"{self.nome} - {self.data_ora_inizio.strftime('%d/%m/%Y %H:%M')}"

    def posti_occupati(self):
        """Restituisce il numero di posti occupati"""
        return self.partecipazione_set.count()

    def posti_liberi(self):
        """Restituisce il numero di posti liberi"""
        return self.posti_disponibili - self.posti_occupati()

    def is_iscrizione_aperta(self):
        """Verifica se l'iscrizione è ancora aperta"""
        return timezone.now() < self.data_ora_inizio and self.posti_liberi() > 0


class Partecipazione(models.Model):

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    data_iscrizione = models.DateTimeField(auto_now_add=True)
    presente = models.BooleanField(default=False, help_text="Segna se il cliente si è presentato all'evento")

    class Meta:
        verbose_name = "Partecipazione"
        verbose_name_plural = "Partecipazioni"
        unique_together = ['cliente', 'evento']

    def __str__(self):
        return f"{self.cliente} partecipa a {self.evento.nome}"


class UtilizzoImpiantoEvento(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    impianto = models.ForeignKey(Impianto, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Utilizzo Impianto per Evento"
        verbose_name_plural = "Utilizzi Impianti per Eventi"
        unique_together = ['evento', 'impianto']

    def __str__(self):
        return f"{self.evento.nome} utilizza {self.impianto.nome}"


class GestioneImpianto(models.Model):

    personale = models.ForeignKey(Personale, on_delete=models.CASCADE)
    impianto = models.ForeignKey(Impianto, on_delete=models.CASCADE)
    data_assegnazione = models.DateField(auto_now_add=True)
    note = models.TextField(blank=True, help_text="Note sulla gestione dell'impianto")

    class Meta:
        verbose_name = "Gestione Impianto"
        verbose_name_plural = "Gestioni Impianti"
        unique_together = ['personale', 'impianto']

    def __str__(self):
        return f"{self.personale} gestisce {self.impianto}"