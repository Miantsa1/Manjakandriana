from django.db import models
from datetime import date

class Arrondissement(models.Model):
    arrondissement_nom = models.CharField(max_length=30)
    arrondissement_numero = models.CharField(max_length=3)
    def __str__(self):
        return f"{self.arrondissement_nom}"