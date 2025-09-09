# historique/models.py
from django.db import models
from django.utils import timezone
from responsable.models import Responsable

class HistoriqueAction(models.Model):
    ACTIONS_CHOIX = [
        ('ajout', 'Ajout'),
        ('modification', 'Modification'),
        ('suppression', 'Suppression'),
        ('validation', 'Validation'),
        ('connexion', 'Connexion'),
        ('autre', 'Autre'),
    ]

    responsable = models.ForeignKey(Responsable, on_delete=models.CASCADE)
    fonction = models.CharField(max_length=50)
    action = models.CharField(max_length=50, choices=ACTIONS_CHOIX)
    description = models.TextField()
    date_action = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.responsable.nom_responsable} - {self.action} ({self.date_action})"
