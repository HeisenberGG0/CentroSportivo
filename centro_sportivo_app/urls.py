# centro_sportivo_app/urls.py

from django.urls import path
from . import views # Importa le viste dalla stessa directory (l'app corrente)
app_name = 'centro_sportivo_app'

urlpatterns = [

    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('gestione-prenotazioni/', views.gestione_prenotazioni, name='gestione_prenotazioni'),

    # Prenotazioni - Clienti
    path('nuova-prenotazione/', views.nuova_prenotazione, name='nuova_prenotazione'),
    path('mie-prenotazioni/', views.mie_prenotazioni, name='mie_prenotazioni'),
    path('prenotazione/<int:prenotazione_id>/modifica/', views.modifica_prenotazione, name='modifica_prenotazione'),
    path('prenotazione/<int:prenotazione_id>/annulla/', views.annulla_prenotazione, name='annulla_prenotazione'),

    # Ricerca disponibilità
    path('ricerca-disponibilita/', views.ricerca_disponibilita, name='ricerca_disponibilita'),

    path('personale/', views.gestione_personale, name='gestione_personale'),


# Eventi
path('eventi/', views.lista_eventi, name='lista_eventi'),
path('eventi/crea/', views.crea_evento, name='crea_evento'),
path('eventi/<int:evento_id>/elimina/', views.elimina_evento, name='elimina_evento'),
path('eventi/<int:evento_id>/iscrizione/', views.iscrizione_evento, name='iscrizione_evento'),
path('eventi/<int:evento_id>/cancella-iscrizione/', views.cancella_iscrizione, name='cancella_iscrizione'),
path('eventi/miei/', views.miei_eventi, name='miei_eventi'),
path('eventi/ricerca/', views.ricerca_eventi, name='ricerca_eventi'),


]
