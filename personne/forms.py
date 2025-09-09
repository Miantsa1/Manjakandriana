from django import forms
from .models import Personne
from arrondissement.models import Arrondissement
from django.forms.widgets import FileInput

class PersonneForm(forms.ModelForm):
    arrondissement = forms.ModelChoiceField(
        queryset=Arrondissement.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="-- Sélectionner un arrodissement --",
        label="Code Arrondissement"
    )

    class Meta:
        model = Personne
        fields = ['nom_personne', 'prenom_personne', 'date_de_naissance', 'lieu_de_naissance',
                  'signe_particulier', 'code_district', 'code_arrondissement', 'numero_sexe', 'numero_cin', 'sexe', 'domicile', 'arrondissement', 'profession', 'pere',
                  'mere', 'date_enregistrement_cin', 'lieu_enregistrement_cin', 'nouveau_nom_personne', 'surnoms_personne', 'commune_personne', 'taille_personne', 'origine', 'service_nationale', 'date_remplacement_cni', 'bon_de_commande', 'arrondissement', 'type_cin', 'photo' ]

    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['code_arrondissement'].widget = forms.HiddenInput()
        if self.instance and self.instance.pk:
            self.fields['arrondissement'].initial = self.instance.arrondissement

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.code_district = "106"

        if instance.arrondissement and not instance.code_arrondissement:
            instance.code_arrondissement = instance.arrondissement.arrondissement_numero

        if commit:
            instance.save()
            self.save_m2m()

        return instance


    def clean(self):
        cleaned_data = super().clean()
        code_arr = cleaned_data.get('arrondissement')
        nom = cleaned_data.get('nom_personne')
        prenom = cleaned_data.get('prenom_personne')
        cni_numero = cleaned_data.get('numero_cin')

        if code_arr:
            cleaned_data['arrondissement'] = code_arr

        if nom and prenom and cni_numero:
            queryset = Personne.objects.filter(
                nom_personne=nom,
                prenom_personne=prenom,
                numero_cin=cni_numero
            )

            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)

            if queryset.exists():
                raise forms.ValidationError("Une personne avec ces informations existe déjà.")
        return cleaned_data

