from django.contrib import admin

from .models import Personne

@admin.register(Personne)
class PersonneAdmin(admin.ModelAdmin):
    list_display = ('nom_personne', 'prenom_personne', 'date_de_naissance', 'lieu_de_naissance', 'signe_particulier', 'code_district', 'code_arrondissement', 'numero_sexe', 'numero_cin', 'sexe', 'domicile', 'arrondissement', 'profession', 'pere', 'mere', 'date_enregistrement_cin', 'lieu_enregistrement_cin', 'nouveau_nom_personne', 'surnoms_personne', 'commune_personne', 'taille_personne', 'origine', 'service_nationale', 'date_remplacement_cni', 'bon_de_commande', 'date_creation', 'responsable', 'est_valide', 'est_exporte_cni', 'type_cin', 'photo')
