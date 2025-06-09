# centro_sportivo_app/forms.py

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, time, timedelta
from .models import Prenotazione, Impianto, Cliente


class PrenotazioneForm(forms.ModelForm):
    """Form per creare/modificare prenotazioni"""

    class Meta:
        model = Prenotazione
        fields = ['impianto', 'data', 'ora_inizio', 'ora_fine']
        widgets = {
            'data': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'min': timezone.now().date().strftime('%Y-%m-%d')
                }
            ),
            'ora_inizio': forms.TimeInput(
                attrs={
                    'type': 'time',
                    'class': 'form-control',
                    'step': '1800'  # Intervalli di 30 minuti
                }
            ),
            'ora_fine': forms.TimeInput(
                attrs={
                    'type': 'time',
                    'class': 'form-control',
                    'step': '1800'  # Intervalli di 30 minuti
                }
            ),
            'impianto': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            )
        }
        labels = {
            'impianto': 'Seleziona Impianto',
            'data': 'Data Prenotazione',
            'ora_inizio': 'Ora Inizio',
            'ora_fine': 'Ora Fine'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mostra solo impianti disponibili
        self.fields['impianto'].queryset = Impianto.objects.filter(
            stato='disponibile'
        ).order_by('tipologia', 'nome')

        # Migliora la visualizzazione degli impianti
        self.fields['impianto'].empty_label = "--- Seleziona un impianto ---"

    def clean_data(self):
        """Valida che la data non sia nel passato"""
        data = self.cleaned_data.get('data')
        if data and data < timezone.now().date():
            raise ValidationError("Non puoi prenotare per una data passata.")
        return data

    def clean_ora_fine(self):
        """Valida che l'ora di fine sia successiva a quella di inizio"""
        ora_inizio = self.cleaned_data.get('ora_inizio')
        ora_fine = self.cleaned_data.get('ora_fine')

        if ora_inizio and ora_fine:
            if ora_fine <= ora_inizio:
                raise ValidationError("L'ora di fine deve essere successiva all'ora di inizio.")

            # Controlla che la durata non superi le 4 ore
            durata = datetime.combine(timezone.now().date(), ora_fine) - \
                     datetime.combine(timezone.now().date(), ora_inizio)
            if durata > timedelta(hours=4):
                raise ValidationError("La durata massima di una prenotazione è di 4 ore.")

        return ora_fine

    def clean(self):
        """Validazioni aggiuntive sui dati combinati"""
        cleaned_data = super().clean()
        impianto = cleaned_data.get('impianto')
        data = cleaned_data.get('data')
        ora_inizio = cleaned_data.get('ora_inizio')
        ora_fine = cleaned_data.get('ora_fine')

        if impianto and data and ora_inizio and ora_fine:
            # Controlla la disponibilità dell'impianto
            if not impianto.is_disponibile(data, ora_inizio, ora_fine):
                raise ValidationError(
                    f"L'impianto {impianto.nome} non è disponibile "
                    f"per la fascia oraria selezionata."
                )

            # Controlla orari di apertura (es: 7:00 - 23:00)
            orario_apertura = time(7, 0)
            orario_chiusura = time(23, 0)

            if ora_inizio < orario_apertura or ora_fine > orario_chiusura:
                raise ValidationError(
                    f"Gli orari di prenotazione devono essere compresi "
                    f"tra le {orario_apertura.strftime('%H:%M')} e le "
                    f"{orario_chiusura.strftime('%H:%M')}."
                )

        return cleaned_data


class FiltroPrenotazioniForm(forms.Form):
    """Form per filtrare le prenotazioni nella gestione"""

    STATO_CHOICES = [
        ('', 'Tutti gli stati'),
        ('attesa', 'In Attesa'),
        ('annullata', 'Annullata'),
    ]

    stato = forms.ChoiceField(
        choices=STATO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    data_da = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        label='Data Da'
    )

    data_a = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        label='Data A'
    )

    impianto = forms.ModelChoiceField(
        queryset=Impianto.objects.all().order_by('tipologia', 'nome'),
        required=False,
        empty_label="Tutti gli impianti",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    cliente = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome o username cliente...'
        }),
        label='Cliente'
    )


class RicercaDisponibilitaForm(forms.Form):
    """Form per ricercare la disponibilità degli impianti"""

    TIPOLOGIA_CHOICES = [
        ('', 'Tutte le tipologie'),
        ('calcio', 'Campo da Calcio'),
        ('tennis', 'Campo da Tennis'),
        ('padel', 'Campo da Padel'),
        ('basket', 'Campo da Basket'),
        ('pallavolo', 'Campo da Pallavolo'),
    ]

    data = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'min': timezone.now().date().strftime('%Y-%m-%d')
        }),
        label='Data',
        initial=timezone.now().date()
    )

    tipologia = forms.ChoiceField(
        choices=TIPOLOGIA_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Tipologia Impianto'
    )

    ora_inizio = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'class': 'form-control',
            'step': '1800'
        }),
        label='Ora Inizio',
        initial=time(9, 0)
    )

    ora_fine = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'class': 'form-control',
            'step': '1800'
        }),
        label='Ora Fine',
        initial=time(11, 0)
    )

    def clean_data(self):
        """Valida che la data non sia nel passato"""
        data = self.cleaned_data.get('data')
        if data and data < timezone.now().date():
            raise ValidationError("Non puoi cercare disponibilità per date passate.")
        return data

    def clean_ora_fine(self):
        """Valida che l'ora di fine sia successiva a quella di inizio"""
        ora_inizio = self.cleaned_data.get('ora_inizio')
        ora_fine = self.cleaned_data.get('ora_fine')

        if ora_inizio and ora_fine and ora_fine <= ora_inizio:
            raise ValidationError("L'ora di fine deve essere successiva all'ora di inizio.")

        return ora_fine
