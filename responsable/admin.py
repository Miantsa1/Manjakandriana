from django.contrib import admin

from .models import Responsable

@admin.register(Responsable)
class ResponsableAdmin(admin.ModelAdmin):
    list_display =('nom_responsable', 'prenom_responsable', 'mot_de_passe', 'arrondissement', 'email', 'date_enregistrement', 'image_responsable', 'fonction')

