from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from responsable import views as responsable_views
from personne import views as personne_views # ← Importer les vues

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', responsable_views.SeConnecter.as_view(), name='login'),
    #path('', personne_views.carte_madagascar, name='carte'),  # ← Page d'accueil = carte
    path('personne/', include('personne.urls')),
    path('arrondissement/', include('arrondissement.urls')),
    path('responsable/', include('responsable.urls')),
    
]
