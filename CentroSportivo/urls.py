
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin', admin.site.urls),
    # Includi gli URL della tua app con il prefisso 'app/'.
    path('', include('centro_sportivo_app.urls')),

]