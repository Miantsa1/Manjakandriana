from django.shortcuts import render, redirect, HttpResponse
from .models import Arrondissement
from django.views import View

from .forms import ArrondissementForm
from django.contrib import messages

def index(request, *args, **kwargs):
    liste_arrondissement = Arrondissement.objects.all()
    context = {
        'arrondissements' : liste_arrondissement,
        'district_nom' : 'Nom du District',
    }
    return render(request, 'arrondissements/indexArrondissement.html', context)

class CreateArrondissement(View):
    def get(self, request, *args, **kwargs):
        form = ArrondissementForm()
        return render(request, 'arrondissements/create_arrondissement.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = ArrondissementForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Arrondissement enregistré avec succès')
            return redirect('arrondissements:indexArrondissement')
        else:
            messages.error(request, 'Erreur lors de l\'enregistrement du nouveau District')


class DeleteArrondissement(View):
    def post(self, request, pk, *args, **kwargs):
        try:
            arrondissement = Arrondissement.objects.get(pk=pk)
            arrondissement.delete()
            messages.success(request, 'Arrondissement supprimé avec succès')
        except Arrondissement.DoesNotExist:
            messages.error(request, 'Arrondissement introuvable')
        return redirect('arrondissements:indexArrondissement')

class UpdateArrondissement(View):
    def get(self, request, pk, *args, **kwargs):
        arrondissement = Arrondissement.objects.get(pk=pk)
        form = ArrondissementForm(instance=arrondissement)
        return render(request, 'arrondissements/arrondissementUpdate.html', {'form': form})

    def post(self, request, pk, *args, **kwargs):
        arrondissement = Arrondissement.objects.get(pk=pk)
        form = ArrondissementForm(request.POST, instance=arrondissement)
        if form.is_valid():
            form.save()
            messages.success(request, 'Arrondissement bien modifié avec succès')
            return redirect('arrondissements:indexArrondissement') 
        else:
            messages.error(request, 'Erreur lors de la modification')
            return render(request, 'arrondissements/arrondissementUpdate.html', {'form': form})   