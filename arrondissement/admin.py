from django.contrib import admin

from .models import Arrondissement

@admin.register(Arrondissement)
class ArrondissementAdmin(admin.ModelAdmin):
    list_display = ('arrondissement_nom', 'arrondissement_numero')

