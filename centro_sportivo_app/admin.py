from django.contrib import admin
from .models import Impianto, Cliente, Personale, Prenotazione, Evento, Partecipazione, UtilizzoImpiantoEvento, GestioneImpianto

admin.site.register(Impianto)
admin.site.register(Cliente)
admin.site.register(Personale)
admin.site.register(Prenotazione)
admin.site.register(Evento)
admin.site.register(Partecipazione)
admin.site.register(UtilizzoImpiantoEvento)
admin.site.register(GestioneImpianto)