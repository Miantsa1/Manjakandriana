from django import forms
from .models import Arrondissement

class ArrondissementForm(forms.ModelForm):
    class Meta:
        model = Arrondissement
        fields = ['arrondissement_nom', 'arrondissement_numero']
    
    def clean(self):
        cleaned_data = super().clean()
        nom = cleaned_data.get('arrondissement_nom')
        numero = cleaned_data.get('arrondissement_numero')

        if nom and numero:
            queryset = Arrondissement.objects.filter(
                arrondissement_nom=nom,
                arrondissement_numero=numero
            )

            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)

            if queryset.exists():
                raise forms.ValidationError("Un Arrondissement avec ces informations existe déjà.")
        return cleaned_data
