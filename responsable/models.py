from django.db import models
from django.utils import timezone

class Responsable(models.Model):
    nom_responsable = models.CharField(max_length=100)
    prenom_responsable = models.CharField(max_length=200)
    arrondissement = models.ForeignKey('arrondissement.Arrondissement', on_delete=models.CASCADE)
    email = models.CharField(max_length=100)
    mot_de_passe = models.CharField(max_length=100)
    date_enregistrement = models.DateField(auto_now_add=True)
    image_responsable = models.ImageField(upload_to='static/assets/img/', blank=True, null=True)
    FONCTION_CHOICES = [
            ('district', 'Chef de District'),
            ('arrondissement', 'Chef d\'Arrondissement'),
        ]
    fonction = models.CharField(max_length=20, choices=FONCTION_CHOICES, blank=True, null=True)

    def __str__(self):
        return f"{self.nom_responsable} {self.prenom_responsable} {self.mot_de_passe} {self.email} {self.arrondissement.arrondissement_nom}"

    def get_image_url(self):
        if self.image_responsable:
            return self.image_responsable.url 
        return None

class Notification(models.Model):
    titre = models.CharField(max_length=255)
    message = models.TextField()
    icone = models.CharField(max_length=50, default="bx bx-info-circle")
    url = models.URLField(blank=True, null=True)
    est_lue = models.BooleanField(default=False)
    date_creation = models.DateTimeField(default=timezone.now)
    destinataire = models.ForeignKey('Responsable', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.titre} - {self.destinataire}"

