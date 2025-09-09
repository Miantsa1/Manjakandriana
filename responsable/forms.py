from django import forms
from .models import Responsable
from arrondissement.models import Arrondissement
from django.forms.widgets import FileInput

class ResponsableForm(forms.ModelForm):
    arrondissement = forms.ModelChoiceField(
        queryset=Arrondissement.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="-- Sélectionner un arrondissement --"        
    )
    class Meta:
        model = Responsable
        fields = ['nom_responsable', 'prenom_responsable', 'email', 'mot_de_passe', 'arrondissement', 'image_responsable']

    def clean(self):
        cleaned_data = super().clean()
        nom = cleaned_data.get('nom_responsable')
        prenom = cleaned_data.get('prenom_responsable')
        
        if nom and prenom:
            queryset = Responsable.objects.filter(
                nom_responsable=nom,
                prenom_responsable=prenom
            )

            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)

            if queryset.exists():
                raise forms.ValidationError("Une responsable avec ces informations existe déjà")
        return cleaned_data

class EmailForm(forms.Form):
    to_email = forms.EmailField(label="Destinataire")
    subject = forms.CharField(label="Objet", max_length=255)
    message = forms.CharField(widget=forms.Textarea, label="Contenu")
    
