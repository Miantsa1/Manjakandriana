from django.db import models
from django.utils import timezone
from responsable.models import Responsable

 
class Personne(models.Model):
    SEXE_CHOIX = [
        ('Homme', 'homme'),
        ('Femme', 'femme'),
    ]

    TypeCNI_Choix = [
        ('primata', 'primata'),
        ('duplicata', 'duplicata'),
    ]
    nom_personne = models.CharField(max_length=100)
    prenom_personne = models.CharField(max_length=250)
    date_de_naissance = models.CharField(max_length=50)
    lieu_de_naissance = models.CharField(max_length=200)
    signe_particulier = models.CharField(max_length=200, blank=True, null=True)
    numero_sexe =  models.CharField(max_length=1)
    numero_cin =  models.CharField(max_length=6)
    est_valide = models.BooleanField(default=False)
    sexe = models.CharField(max_length=10, choices=SEXE_CHOIX)
    domicile = models.CharField(max_length=200)
    #arrondissement = models.ForeignKey('arrondissement.Arrondissement', on_delete=models.CASCADE)
    profession = models.CharField(max_length=200)
    pere = models.CharField(max_length=300)
    mere = models.CharField(max_length=300)
    date_enregistrement_cin = models.CharField(max_length=100)
    lieu_enregistrement_cin = models.CharField(max_length=100)

    nouveau_nom_personne = models.CharField(max_length=200, blank=True, null=True)
    surnoms_personne = models.CharField(max_length=150, blank=True, null=True)
    commune_personne = models.CharField(max_length=150, blank=True, null=True)
    taille_personne = models.CharField(max_length=200)
    origine = models.CharField(max_length=100)
    service_nationale = models.CharField(max_length=50, blank=True, null=True)
    date_remplacement_cni = models.CharField(max_length=50, blank=True, null=True)
    bon_de_commande = models.CharField(max_length=50)
    est_exporte_cni = models.BooleanField(default=False)
    date_creation = models.DateField(auto_now_add=True)
    date_modification = models.DateField(auto_now=True) 
    responsable = models.ForeignKey(Responsable, on_delete=models.CASCADE, null=True)
    code_district = models.CharField(max_length=10, blank=True)
    code_arrondissement = models.CharField(max_length=10, blank=True)
    arrondissement = models.ForeignKey('arrondissement.Arrondissement', on_delete=models.SET_NULL, null=True)
    type_cin = models.CharField(max_length=10, choices=TypeCNI_Choix, blank= True)
    photo = models.ImageField(upload_to="static/assets/img/",  blank=True, null=True)
    def save(self, *args, **kwargs):
        self.code_district = "106"
        if self.arrondissement and not self.code_arrondissement:
            self.code_arrondissement = self.arrondissement.arrondissement_numero
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nom_personne} {self.prenom_personne} {self.arrondissement.arrondissement_nom} "

