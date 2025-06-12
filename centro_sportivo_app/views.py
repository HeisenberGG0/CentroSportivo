from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q, Count, Avg
from datetime import datetime, timedelta
from .models import Cliente, Personale, Impianto, Prenotazione, Evento
from .forms import PrenotazioneForm, FiltroPrenotazioniForm, RicercaDisponibilitaForm



def index(request):
    """Homepage del sito"""
    return render(request, 'centro_sportivo_app/index.html')


def login_view(request):
    """View per il login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Prova con Cliente
        try:
            cliente = Cliente.objects.get(username=username, is_active=True)
            if cliente.check_password(password):
                # Login riuscito, salva i dati nella sessione
                request.session['user_id'] = cliente.pk
                request.session['user_type'] = 'cliente'
                request.session['username'] = cliente.username
                request.session['full_name'] = cliente.get_full_name()

                cliente.ultimo_accesso = timezone.now()
                cliente.save()

                messages.success(request, f'Benvenuto {cliente.get_full_name()}!')
                return redirect('centro_sportivo_app:dashboard')
        except Cliente.DoesNotExist:
            pass

         # Prova con personale
        try:
            personale = Personale.objects.get(username=username, is_active=True)
            if personale.check_password(password):
                # Login riuscito, salva dati nella sessione
                request.session['user_id'] = personale.pk
                request.session['user_type'] = 'personale'
                request.session['username'] = personale.username
                request.session['full_name'] = personale.get_full_name()

                personale.ultimo_accesso = timezone.now()
                personale.save()

                messages.success(request, f'Benvenuto {personale.get_full_name()}!')
                return redirect('centro_sportivo_app:dashboard')
        except Personale.DoesNotExist:
            pass

        # Se arriviamo qui vuol dire login fallito
        messages.error(request, 'Username o password non corretti.')

    return render(request, 'centro_sportivo_app/login.html')


def logout_view(request):
    """View per il logout"""
    # Cancella i dati dalla sessione
    for key in ['user_id', 'user_type', 'username', 'full_name']:
        if key in request.session:
            del request.session[key]

    messages.success(request, 'Logout effettuato con successo.')
    return redirect('centro_sportivo_app:index')


def register_view(request):
    """View per la registrazione dei nuovi clienti"""
    if request.method == 'POST':
        username = request.POST.get('username')
        nome = request.POST.get('nome')
        cognome = request.POST.get('cognome')
        email = request.POST.get('email')
        telefono = request.POST.get('telefono', '')
        password = request.POST.get('password')
        codice_fiscale = request.POST.get('codice_fiscale', '')

        # Verifica che username ed email non esistano già
        if Cliente.objects.filter(username=username).exists():
            messages.error(request, 'Username già esistente.')
            return render(request, 'centro_sportivo_app/register.html')

        if Cliente.objects.filter(email=email).exists():
            messages.error(request, 'Email già registrata.')
            return render(request, 'centro_sportivo_app/register.html')
        #Verifica che l'email rispetti il formato corretto
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Il formato dell\'email non è valido.')
            return render(request, 'centro_sportivo_app/register.html')

        # Crea il nuovo cliente
        cliente = Cliente(
            username=username,
            nome=nome,
            cognome=cognome,
            email=email,
            telefono=telefono,
            codice_fiscale=codice_fiscale
        )
        cliente.set_password(password)  # Questa funzione cripta la password
        cliente.save()

        messages.success(request, 'Registrazione completata! Ora puoi fare login.')
        return redirect('centro_sportivo_app:login')

    return render(request, 'centro_sportivo_app/register.html')


def dashboard(request):
    """Dashboard principale - richiede login"""
    # Verifica se l'utente è loggato
    if 'user_id' not in request.session:
        messages.error(request, 'Devi fare login per accedere.')
        return redirect('centro_sportivo_app:login')

    user_type = request.session.get('user_type')
    user_id = request.session.get('user_id')

    context = {
        'user_type': user_type,
    }

    # Ottieni l'oggetto utente e calcola le statistiche
    if user_type == 'cliente':
        try:
            utente = Cliente.objects.get(pk=user_id)

            # Calcola statistiche cliente
            prenotazioni_attesa = Prenotazione.objects.filter(
                cliente=utente,
                stato__in=['attesa', 'annullata'],
                data__gte=timezone.now().date()
            ).count()

            eventi_iscritto = Partecipazione.objects.filter(cliente=utente).count()

            # Ottieni attività recenti
            prenotazioni_recenti = Prenotazione.objects.filter(
                cliente=utente
            ).order_by('-data_creazione')[:5]

            partecipazioni_recenti = Partecipazione.objects.filter(
                cliente=utente
            ).order_by('-data_iscrizione')[:5]

            # Combina le attività recenti
            attivita_recenti = []

            for p in prenotazioni_recenti:
                attivita_recenti.append({
                    'tipo': 'prenotazione',
                    'titolo': f"Prenotazione {p.impianto.nome}",
                    'data': p.data,
                    'orario': f"{p.ora_inizio.strftime('%H:%M')}-{p.ora_fine.strftime('%H:%M')}",
                    'stato': p.stato,
                    'data_creazione': p.data_creazione,
                    'id': p.id
                })

            for p in partecipazioni_recenti:
                attivita_recenti.append({
                    'tipo': 'evento',
                    'titolo': p.evento.nome,
                    'data': p.evento.data_ora_inizio.date(),
                    'orario': f"{p.evento.data_ora_inizio.strftime('%H:%M')}-{p.evento.data_ora_fine.strftime('%H:%M')}",
                    'stato': 'iscritto',
                    'data_creazione': p.data_iscrizione,
                    'id': p.evento.id
                })

            # Ordina per data di creazione decrescente
            attivita_recenti = sorted(attivita_recenti, key=lambda x: x['data_creazione'], reverse=True)[:5]

            # Aggiungi al contesto
            context.update({
                'utente': utente,
                'prenotazioni_attesa': prenotazioni_attesa,
                'eventi_iscritto': eventi_iscritto,
                'attivita_recenti': attivita_recenti
            })

        except Cliente.DoesNotExist:
            messages.error(request, 'Utente non trovato.')
            return redirect('centro_sportivo_app:login')

    elif user_type == 'personale':
        try:
            utente = Personale.objects.get(pk=user_id)

            # Calcola statistiche personale
            prenotazioni_gestite = Prenotazione.objects.filter(
                gestita_da=utente
            ).count()

            eventi_organizzati = Evento.objects.filter(
                organizzatore=utente
            ).count()

            # Recupera attività recenti
            prenotazioni_recenti = Prenotazione.objects.filter(
                gestita_da=utente
            ).order_by('-data_creazione')[:5]

            eventi_recenti = Evento.objects.filter(
                organizzatore=utente
            ).order_by('-data_creazione')[:5]

            # Combina le attività recenti
            attivita_recenti = []

            for p in prenotazioni_recenti:
                attivita_recenti.append({
                    'tipo': 'prenotazione',
                    'titolo': "Prenotazione confermata",
                    'dettaglio': f"Cliente: {p.cliente.get_full_name()} - {p.impianto.nome}",
                    'data': p.data,
                    'data_creazione': p.data_creazione,
                    'id': p.id,
                    'tempo_fa': timezone.now() - ( p.data_creazione)
                })

            for e in eventi_recenti:
                attivita_recenti.append({
                    'tipo': 'evento',
                    'titolo': "Evento creato",
                    'dettaglio': e.nome,
                    'data': e.data_ora_inizio.date(),
                    'data_creazione': e.data_creazione,
                    'id': e.id,
                    'tempo_fa': timezone.now() - e.data_creazione
                })

            # Ordina per data di creazione decrescente
            attivita_recenti = sorted(attivita_recenti, key=lambda x: x['data_creazione'], reverse=True)[:5]

            # Formatta i tempi in modo leggibile
            for attivita in attivita_recenti:
                ore = attivita['tempo_fa'].total_seconds() // 3600
                if ore < 24:
                    attivita['tempo_leggibile'] = f"{int(ore)} ore fa"
                else:
                    giorni = int(ore // 24)
                    attivita['tempo_leggibile'] = f"{giorni} {'giorno' if giorni == 1 else 'giorni'} fa"

            # Aggiungi al contesto
            context.update({
                'utente': utente,
                'prenotazioni_gestite': prenotazioni_gestite,
                'eventi_organizzati': eventi_organizzati,
                'attivita_recenti': attivita_recenti
            })

        except Personale.DoesNotExist:
            messages.error(request, 'Utente non trovato.')
            return redirect('centro_sportivo_app:login')
    else:
        messages.error(request, 'Tipo utente non valido.')
        return redirect('centro_sportivo_app:login')

    return render(request, 'centro_sportivo_app/dashboard.html', context)

def get_current_user(request):
    """Funzione di aiuto per ottenere l'utente corrente e che poi verra riutilizzata"""
    if 'user_id' not in request.session or 'user_type' not in request.session:
        return None, None

    user_id = request.session['user_id']
    user_type = request.session['user_type']

    try:
        if user_type == 'cliente':
            user_obj = Cliente.objects.get(pk=user_id, is_active=True)
        elif user_type == 'personale':
            user_obj = Personale.objects.get(pk=user_id, is_active=True)
        else:
            return None, None

        return user_obj, user_type
    except (Cliente.DoesNotExist, Personale.DoesNotExist):
        return None, None


def gestione_prenotazioni(request):
    """View per gestire le prenotazioni riservata al personale"""
    utente, user_type = get_current_user(request)

    if not utente or user_type != 'personale':
        messages.error(request, 'Accesso riservato al personale.')
        return redirect('centro_sportivo_app:login')

    # Query base delle prenotazioni
    prenotazioni = Prenotazione.objects.all().order_by('-data_creazione')

    #  Filtro per impianto
    impianto_id = request.GET.get('impianto')
    if impianto_id:
        prenotazioni = prenotazioni.filter(impianto_id=impianto_id)

    # Filtro per stato
    stato = request.GET.get('stato')
    if stato:
        prenotazioni = prenotazioni.filter(stato=stato)

    #  Lista degli impianti
    impianti = Impianto.objects.all().order_by('nome')

    prenotazioni_in_attesa = Prenotazione.objects.filter(stato='attesa').count()
    prenotazioni_annullate = Prenotazione.objects.filter(stato='annullata').count()
    totale_prenotazioni = Prenotazione.objects.count()

    context = {
        'prenotazioni': prenotazioni,
        'utente': utente,
        'impianti': impianti,
        'impianto_selezionato': impianto_id,
        'stato_selezionato': stato,
        'prenotazioni_in_attesa': prenotazioni_in_attesa,
        'prenotazioni_annullate': prenotazioni_annullate,
        'totale_prenotazioni': totale_prenotazioni,
    }

    return render(request, 'centro_sportivo_app/gestione_prenotazioni.html', context)


def nuova_prenotazione(request):
    """View per creare una nuova prenotazione dai clienti"""
    utente, user_type = get_current_user(request)

    if not utente or user_type != 'cliente':
        messages.error(request, 'Devi essere un cliente registrato per prenotare.')
        return redirect('centro_sportivo_app:login')

    if request.method == 'POST':
        form = PrenotazioneForm(request.POST)
        if form.is_valid():
            prenotazione = form.save(commit=False)
            prenotazione.cliente = utente

            # Calcola l'importo totale
            durata_ore = prenotazione.durata_ore()
            prenotazione.importo_totale = durata_ore * float(prenotazione.impianto.tariffa_oraria)

            # Associa automaticamente un responsabile prenotazioni in modo casuale
            try:
                import random

                responsabili = Personale.objects.filter(
                    ruolo='responsabile_prenotazioni',
                    is_active=True
                )

                if responsabili.exists():
                    # Selezione casuale tra i responsabili disponibili
                    responsabile = random.choice(list(responsabili))
                    prenotazione.gestita_da = responsabile
                else:
                    # Gestione caso in cui non ci sia nessun responsabile attivo
                    messages.warning(request, 'Nessun responsabile prenotazioni disponibile al momento.')
            except Exception as e:
                messages.error(request, f'Errore nell\'assegnazione del responsabile: {e}')

            prenotazione.save()
            #mi prendo il nome del responsabile associato per mostrarlo
            responsabile_nome = prenotazione.gestita_da.get_full_name() if prenotazione.gestita_da else "Non assegnato"
            messages.success(
                request,
                f'Prenotazione creata con successo! '
                f'Importo totale: €{prenotazione.importo_totale:.2f}\n'
                f'Responsabile associato: {responsabile_nome}'
            )
            return redirect('centro_sportivo_app:mie_prenotazioni')
    else:
        form = PrenotazioneForm()

    context = {
        'form': form,
        'utente': utente,
        'user_type': user_type,
    }

    return render(request, 'centro_sportivo_app/nuova_prenotazione.html', context)

def mie_prenotazioni(request):
    """View per visualizzare le prenotazioni del cliente"""
    utente, user_type = get_current_user(request)

    if not utente or user_type != 'cliente':
        messages.error(request, 'Accesso riservato ai clienti.')
        return redirect('centro_sportivo_app:login')

    prenotazioni = Prenotazione.objects.filter(
        cliente=utente
    ).order_by('-data', '-ora_inizio')

    # Filtra le prenotazioni per stato
    prenotazioni_attesa = prenotazioni.filter(stato='attesa')
    prenotazioni_annullate = prenotazioni.filter(stato='annullata')

    # Statistiche per il cliente
    stats = {
        'totali': prenotazioni.count(),
        'attesa': prenotazioni_attesa.count(),
        'annullate': prenotazioni_annullate.count(),
    }

    context = {
        'prenotazioni': prenotazioni,
        'prenotazioni_attesa': prenotazioni_attesa,
        'prenotazioni_annullate': prenotazioni_annullate,
        'stats': stats,
        'utente': utente,
        'user_type': user_type,
    }

    return render(request, 'centro_sportivo_app/mie_prenotazioni.html', context)

def modifica_prenotazione(request, prenotazione_id):
    """View per modificare una prenotazione esistente"""
    utente, user_type = get_current_user(request)

    if not utente:
        messages.error(request, 'Devi essere autenticato.')
        return redirect('centro_sportivo_app:login')

    prenotazione = get_object_or_404(Prenotazione, id=prenotazione_id)

    # Controlla i permessi
    if user_type == 'cliente' and prenotazione.cliente != utente:
        messages.error(request, 'Non puoi modificare prenotazioni di altri clienti.')
        return redirect('centro_sportivo_app:mie_prenotazioni')
    elif user_type == 'personale' and utente.ruolo not in ['manager', 'responsabile_prenotazioni']:
        messages.error(request, 'Non hai i permessi per modificare le prenotazioni.')
        return redirect('centro_sportivo_app:gestione_prenotazioni')

    # Non permettere modifiche per prenotazioni gia annullate
    if prenotazione.stato in [ 'annullata']:
        messages.error(request, 'Non puoi modificare prenotazioni già annullate.')
        return redirect('centro_sportivo_app:mie_prenotazioni' if user_type == 'cliente'
                        else 'centro_sportivo_app:gestione_prenotazioni')

    if request.method == 'POST':
        form = PrenotazioneForm(request.POST, instance=prenotazione)
        if form.is_valid():
            prenotazione = form.save(commit=False)

            # Ricalcola l'importo
            durata_ore = prenotazione.durata_ore()
            prenotazione.importo_totale = durata_ore * float(prenotazione.impianto.tariffa_oraria)

            # Se modificata dal personale, segna chi l'ha gestita
            if user_type == 'personale':
                prenotazione.gestita_da = utente

            prenotazione.save()

            messages.success(request, 'Prenotazione modificata con successo!')
            return redirect('centro_sportivo_app:mie_prenotazioni' if user_type == 'cliente'
                            else 'centro_sportivo_app:gestione_prenotazioni')
    else:
        form = PrenotazioneForm(instance=prenotazione)

    context = {
        'form': form,
        'prenotazione': prenotazione,
        'utente': utente,
        'user_type': user_type,
    }

    return render(request, 'centro_sportivo_app/modifica_prenotazione.html', context)


def annulla_prenotazione(request, prenotazione_id):
    """View per annullare una prenotazione"""
    utente, user_type = get_current_user(request)

    if not utente:
        messages.error(request, 'Devi essere autenticato.')
        return redirect('centro_sportivo_app:login')

    prenotazione = get_object_or_404(Prenotazione, id=prenotazione_id)

    # Controlla i permessi dell'utente
    if user_type == 'cliente' and prenotazione.cliente != utente:
        messages.error(request, 'Non puoi annullare prenotazioni di altri clienti.')
        return redirect('centro_sportivo_app:mie_prenotazioni')
    elif user_type == 'personale' and utente.ruolo not in ['manager', 'responsabile_prenotazioni']:
        messages.error(request, 'Non hai i permessi per annullare le prenotazioni.')
        return redirect('centro_sportivo_app:gestione_prenotazioni')

    if prenotazione.stato in ['annullata']:
        messages.warning(request, 'Questa prenotazione è già stata annullata.')
    else:
        prenotazione.stato = 'annullata'
        if user_type == 'personale':
            prenotazione.gestita_da = utente
        prenotazione.save()

        messages.success(request, 'Prenotazione annullata con successo.')

    return redirect('centro_sportivo_app:mie_prenotazioni' if user_type == 'cliente'
                    else 'centro_sportivo_app:gestione_prenotazioni')


def ricerca_disponibilita(request):
    """View per ricercare la disponibilità degli impianti"""
    form = RicercaDisponibilitaForm(request.GET or None)
    impianti_disponibili = []
    impianti_occupati = []

    if form.is_valid():
        data = form.cleaned_data['data']
        tipologia = form.cleaned_data['tipologia']
        ora_inizio = form.cleaned_data['ora_inizio']
        ora_fine = form.cleaned_data['ora_fine']

        # Filtra gli impianti per tipologia
        impianti_query = Impianto.objects.filter(stato='disponibile')
        if tipologia:
            impianti_query = impianti_query.filter(tipologia=tipologia)

        # Controlla la disponibilità di ogni impianto
        for impianto in impianti_query:
            # verifica manualmente la disponibilità
            prenotazioni_sovrapposte = impianto.prenotazione_set.filter(
                data=data,
                stato__in=['attesa']
            ).filter(
                Q(ora_inizio__lt=ora_fine) & Q(ora_fine__gt=ora_inizio)
            )

            if not prenotazioni_sovrapposte.exists():
                # Impianto disponibile
                durata_ore = (datetime.combine(data, ora_fine) -
                              datetime.combine(data, ora_inizio)).total_seconds() / 3600
                importo = durata_ore * float(impianto.tariffa_oraria)

                impianti_disponibili.append({
                    'impianto': impianto,
                    'importo': importo,
                    'durata_ore': durata_ore
                })
            else:
                # Impianto occupato
                impianti_occupati.append({
                    'impianto': impianto,
                    'prenotazioni': prenotazioni_sovrapposte
                })


    context = {
        'form': form,
        'impianti_disponibili': impianti_disponibili,
        'impianti_occupati': impianti_occupati,
    }

    return render(request, 'centro_sportivo_app/ricerca_disponibilita.html', context)


# views.py
def gestione_personale(request):
    """View per mostrare l'organizzazione del personale"""

    # Organizza il personale per ruolo
    personale_per_ruolo = {}

    # prendiamo tutto il personale attivo ordinato per gerarchia
    tutto_personale = Personale.objects.filter(is_active=True).order_by('ruolo', 'cognome')


    for persona in tutto_personale:
        ruolo_display = persona.get_ruolo_display()
        if ruolo_display not in personale_per_ruolo:
            personale_per_ruolo[ruolo_display] = []
        personale_per_ruolo[ruolo_display].append(persona)


    ordine_ruoli = [
        'Manager',
        'Responsabile Prenotazioni',
        'Istruttore',
        'Receptionist',
        'Manutenzione'
    ]

    # Riordina secondo la gerarchia
    personale_ordinato = {}
    for ruolo in ordine_ruoli:
        if ruolo in personale_per_ruolo:
            personale_ordinato[ruolo] = personale_per_ruolo[ruolo]


    context = {
        'personale_per_ruolo': personale_ordinato,
        'totale_personale': tutto_personale.count(),
    }

    return render(request, 'centro_sportivo_app/gestione_personale.html', context)















# centro_sportivo_app/views/eventi_views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q, Avg
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from centro_sportivo_app.models import (
    Evento, Cliente, Personale, Partecipazione,
    Impianto, UtilizzoImpiantoEvento
)


# Vista per visualizzare l'elenco degli eventi (pubblica)
def lista_eventi(request):
    tipologia_filtro = request.GET.get('tipologia')

    # query base per eventi futuri
    eventi_futuri = Evento.objects.filter(
        data_ora_inizio__gte=timezone.now()
    )

    # query base per eventi passati
    eventi_passati = Evento.objects.filter(
        data_ora_inizio__lt=timezone.now()
    )

    # Applica il filtro per tipologia basandosi sugli impianti
    if tipologia_filtro:
        eventi_futuri = eventi_futuri.filter(impianti_utilizzati__tipologia=tipologia_filtro)
        eventi_passati = eventi_passati.filter(impianti_utilizzati__tipologia=tipologia_filtro)


    eventi_futuri = eventi_futuri.distinct().order_by('data_ora_inizio')
    eventi_passati = eventi_passati.distinct().order_by('-data_ora_inizio')[:5]

    # Implementa paginazione per gli eventi futuri
    paginator = Paginator(eventi_futuri, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Aggiunge informazioni sul numero di partecipanti per evento
    for evento in page_obj:
        evento.num_partecipanti = evento.partecipazione_set.count()
        evento.posti_rimasti = evento.posti_disponibili - evento.num_partecipanti

    context = {
        'eventi': page_obj,
        'eventi_passati': eventi_passati,
        'pagina_corrente': 'eventi',
        'tipologia_filtro': tipologia_filtro,
    }

    return render(request, 'centro_sportivo_app/lista_eventi.html', context)



# Vista per la creazione di un nuovo evento (solo staff)
def crea_evento(request):

    utente, user_type = get_current_user(request)

    # Verifica che l'utente sia autenticato e faccia parte del personale
    if not utente or user_type != 'personale':
        messages.error(request, "Solo il personale può creare eventi.")
        return redirect('centro_sportivo_app:lista_eventi')

    # Lista di impianti disponibili
    impianti_disponibili = Impianto.objects.filter(stato='disponibile').order_by('tipologia', 'nome')

    if request.method == 'POST':
        # Dati dell'evento
        nome = request.POST.get('nome')
        descrizione = request.POST.get('descrizione')
        data_ora_inizio = request.POST.get('data_ora_inizio')
        data_ora_fine = request.POST.get('data_ora_fine')
        posti_disponibili = request.POST.get('posti_disponibili')
        costo_iscrizione = request.POST.get('costo_iscrizione')
        impianti_ids = request.POST.getlist('impianti')

        # Validazione base
        errori = []

        if not nome:
            errori.append("Il nome dell'evento è obbligatorio.")
        if not descrizione:
            errori.append("La descrizione dell'evento è obbligatoria.")
        if not data_ora_inizio:
            errori.append("La data e ora di inizio sono obbligatorie.")
        if not data_ora_fine:
            errori.append("La data e ora di fine sono obbligatorie.")
        if not posti_disponibili:
            errori.append("Il numero di posti disponibili è obbligatorio.")
        else:
            try:
                posti_disponibili = int(posti_disponibili)
                if posti_disponibili <= 0:
                    errori.append("I posti disponibili devono essere maggiori di zero.")
            except ValueError:
                errori.append("I posti disponibili devono essere un numero intero.")

        if not costo_iscrizione:
            costo_iscrizione = 0
        else:
            try:
                costo_iscrizione = float(costo_iscrizione)
                if costo_iscrizione < 0:
                    errori.append("Il costo di iscrizione non può essere negativo.")
            except ValueError:
                errori.append("Il costo di iscrizione deve essere un numero.")

        if not impianti_ids:
            errori.append("Devi selezionare almeno un impianto per l'evento.")

        # Se ci sono errori, mostra messaggio e torna al form
        if errori:
            for errore in errori:
                messages.error(request, errore)

            context = {
                'impianti_disponibili': impianti_disponibili,
                'form_data': request.POST,
                'errori': errori
            }
            return render(request, 'centro_sportivo_app/crea_evento.html', context)

        # Creazione dell'evento
        try:
            evento = Evento.objects.create(
                organizzatore=utente,
                nome=nome,
                descrizione=descrizione,
                data_ora_inizio=data_ora_inizio,
                data_ora_fine=data_ora_fine,
                posti_disponibili=posti_disponibili,
                costo_iscrizione=costo_iscrizione
            )

            # Associa gli impianti all'evento
            for impianto_id in impianti_ids:
                impianto = Impianto.objects.get(id=impianto_id)
                UtilizzoImpiantoEvento.objects.create(
                    evento=evento,
                    impianto=impianto
                )

            messages.success(request, f"Evento '{evento.nome}' creato con successo!")
            return redirect('centro_sportivo_app:lista_eventi')

        except Exception as e:
            messages.error(request, f"Errore nella creazione dell'evento: {str(e)}")

            context = {
                'impianti_disponibili': impianti_disponibili,
                'form_data': request.POST
            }
            return render(request, 'centro_sportivo_app/crea_evento.html', context)

    # GET request, mostra form vuoto
    context = {
        'impianti_disponibili': impianti_disponibili,
        'now': timezone.now().strftime('%Y-%m-%dT%H:%M')
    }
    return render(request, 'centro_sportivo_app/crea_evento.html', context)




# Vista per l'eliminazione di un evento (solo staff)
def elimina_evento(request, evento_id):
    evento = get_object_or_404(Evento, pk=evento_id)

    # Verifica che l'utente sia loggato nel sistema
    if not request.session.get('user_id'):
        messages.error(request, "Devi essere loggato per eliminare gli eventi.")
        return redirect('centro_sportivo_app:lista_eventi')

    # Verifica che l'utente sia membro del personale
    try:
        personale = Personale.objects.get(id=request.session.get('user_id'))
    except Personale.DoesNotExist:
        messages.error(request, "Solo il personale può eliminare gli eventi.")
        return redirect('centro_sportivo_app:lista_eventi')

    # Verifica che l'utente sia l'organizzatore dell'evento
    if evento.organizzatore != personale:
        messages.error(request, "Puoi eliminare solo gli eventi che hai organizzato.")
        return redirect('centro_sportivo_app:lista_eventi')

    if request.method == 'POST':
        # Controllo di sicurezza: conferma eliminazione
        conferma = request.POST.get('conferma')
        if conferma == 'elimina':
            nome_evento = evento.nome

            evento.delete()

            messages.success(request, f"Evento '{nome_evento}' eliminato con successo.")
            return redirect('centro_sportivo_app:lista_eventi')
        else:
            messages.error(request, "Conferma di eliminazione non valida.")

    # Ottieni il numero di partecipanti
    num_partecipanti = evento.partecipazione_set.count()

    context = {
        'evento': evento,
        'num_partecipanti': num_partecipanti
    }
    return render(request, 'centro_sportivo_app/elimina_evento.html', context)



# Vista per l'iscrizione a un evento (solo clienti)
def iscrizione_evento(request, evento_id):
    evento = get_object_or_404(Evento, pk=evento_id)

    # Verifica che l'utente sia loggato
    if not request.session.get('user_id'):
        messages.error(request, "Devi essere loggato per iscriverti agli eventi.")
        return redirect('centro_sportivo_app:lista_eventi')

    # Verifica che l'utente sia un cliente
    try:
        cliente = Cliente.objects.get(id=request.session.get('user_id'))
    except Cliente.DoesNotExist:
        messages.error(request, "Solo i clienti possono iscriversi agli eventi.")
        return redirect('centro_sportivo_app:lista_eventi')

    # Verifica se l'evento è ancora aperto alle iscrizioni
    if not evento.is_iscrizione_aperta():
        messages.error(request, "Le iscrizioni per questo evento sono chiuse.")
        return redirect('centro_sportivo_app:lista_eventi')

    # Verifica se ci sono ancora posti disponibili
    if evento.posti_liberi() <= 0:
        messages.error(request, "Non ci sono più posti disponibili per questo evento.")
        return redirect('centro_sportivo_app:lista_eventi')

    # Verifica se il cliente è già iscritto
    if evento.partecipanti.filter(id=cliente.id).exists():
        messages.info(request, "Sei già iscritto a questo evento.")
        return redirect('centro_sportivo_app:lista_eventi')

    # Crea l'iscrizione
    if request.method == 'POST':
        try:
            evento.partecipanti.add(cliente)


            messages.success(request, f"Iscrizione all'evento '{evento.nome}' completata con successo!")
            return redirect('centro_sportivo_app:lista_eventi')

        except Exception as e:
            messages.error(request, "Si è verificato un errore durante l'iscrizione. Riprova.")
            return redirect('centro_sportivo_app:lista_eventi')

    # GET request, mostra pagina di conferma iscrizione
    context = {
        'evento': evento,
        'cliente': cliente
    }
    return render(request, 'centro_sportivo_app/conferma_iscrizione.html', context)


# Vista per la cancellazione dell'iscrizione a un evento (solo clienti)

def cancella_iscrizione(request, evento_id):
    evento = get_object_or_404(Evento, pk=evento_id)

    # Verifica che l'utente sia loggato nel sistema
    if not request.session.get('user_id'):
        messages.error(request, "Devi essere loggato per cancellare l'iscrizione.")
        return redirect('centro_sportivo_app:lista_eventi')

    # Verifica che l'utente sia un cliente
    try:
        cliente = Cliente.objects.get(id=request.session.get('user_id'))
    except Cliente.DoesNotExist:
        messages.error(request, "Solo i clienti possono gestire le proprie iscrizioni.")
        return redirect('centro_sportivo_app:lista_eventi')

    # Solo tipo POST è permesso
    if request.method != 'POST':
        messages.error(request, "Metodo non consentito.")
        return redirect('centro_sportivo_app:miei_eventi')

    # Verifica se il cliente è iscritto
    try:
        partecipazione = Partecipazione.objects.get(cliente=cliente, evento=evento)
    except Partecipazione.DoesNotExist:
        messages.error(request, "Non sei iscritto a questo evento.")
        return redirect('centro_sportivo_app:miei_eventi')

    # Verifica se l'evento non è già iniziato
    if evento.data_ora_inizio <= timezone.now():
        messages.error(request, "Non puoi cancellare l'iscrizione a un evento già iniziato.")
        return redirect('centro_sportivo_app:miei_eventi')

    # Cancella l'iscrizione
    partecipazione.delete()
    messages.success(request, f"Iscrizione all'evento '{evento.nome}' cancellata con successo.")
    return redirect('centro_sportivo_app:miei_eventi')


def miei_eventi(request):
    # Verifica che l'utente sia loggato nel tuo sistema personalizzato
    if not request.session.get('user_id'):
        messages.error(request, "Devi essere loggato per vedere i tuoi eventi.")
        return redirect('centro_sportivo_app:lista_eventi')

    # Verifica che sia un cliente (non staff)
    if request.session.get('is_staff'):
        messages.error(request, "Solo i clienti possono vedere i propri eventi.")
        return redirect('centro_sportivo_app:lista_eventi')

    # Verifica che l'utente sia un cliente
    try:
        cliente = Cliente.objects.get(id=request.session.get('user_id'))
    except Cliente.DoesNotExist:
        messages.error(request, "Questa funzionalità è disponibile solo per i clienti.")
        return redirect('centro_sportivo_app:lista_eventi')

    # Ottieni eventi futuri a cui il cliente è iscritto
    eventi_futuri = Evento.objects.filter(
        partecipazione__cliente=cliente,
        data_ora_inizio__gte=timezone.now()
    ).order_by('data_ora_inizio')

    # Ottieni eventi passati a cui il cliente ha partecipato
    eventi_passati = Evento.objects.filter(
        partecipazione__cliente=cliente,
        data_ora_inizio__lt=timezone.now()
    ).order_by('-data_ora_inizio')

    # Aggiungi informazioni sulla presenza per gli eventi passati
    for evento in eventi_passati:
        try:
            partecipazione = Partecipazione.objects.get(evento=evento, cliente=cliente)
            evento.presente = partecipazione.presente
        except Partecipazione.DoesNotExist:
            evento.presente = False

    context = {
        'cliente': cliente,
        'eventi_futuri': eventi_futuri,
        'eventi_passati': eventi_passati,
        'now': timezone.now()
    }
    return render(request, 'centro_sportivo_app/miei_eventi.html', context)



# Vista per ricercare gli eeventi
def ricerca_eventi(request):
    query = request.GET.get('q', '')
    tipo = request.GET.get('tipo', '')
    data_da = request.GET.get('data_da', '')
    data_a = request.GET.get('data_a', '')

    # Base query
    eventi = Evento.objects.all()

    # Filtra per nome o descrizione
    if query:
        eventi = eventi.filter(
            Q(nome__icontains=query) | Q(descrizione__icontains=query)
        )

    # Filtra per tipo di impianto
    if tipo:
        eventi = eventi.filter(impianti_utilizzati__tipologia=tipo).distinct()

    # Filtra per data
    if data_da:
        eventi = eventi.filter(data_ora_inizio__gte=data_da)

    if data_a:
        eventi = eventi.filter(data_ora_inizio__lte=data_a)

    # Ordina per data di inizio
    eventi = eventi.order_by('data_ora_inizio')

    # Aggiungi informazioni sul numero di partecipanti
    for evento in eventi:
        evento.num_partecipanti = evento.partecipazione_set.count()
        evento.posti_rimasti = evento.posti_disponibili - evento.num_partecipanti

    # Lista dei tipi di impianti disponibili per il filtro
    tipi_impianto = Impianto.TIPOLOGIA_CHOICES

    context = {
        'eventi': eventi,
        'query': query,
        'tipo_selezionato': tipo,
        'data_da': data_da,
        'data_a': data_a,
        'tipi_impianto': tipi_impianto,
        'num_risultati': eventi.count()
    }
    return render(request, 'centro_sportivo_app/ricerca_eventi.html', context)