from django.shortcuts import render, redirect, HttpResponse
from .models import Responsable
from .models import Notification
from django.views import View
from .forms import ResponsableForm, EmailForm
from django.contrib import messages
import io
from django.core.mail import EmailMessage
from arrondissement.models import Arrondissement
from django.shortcuts import render, redirect
from .utils import decrypt_password
from django.shortcuts import get_object_or_404, redirect
from .utils import encrypt_password

def index(request, *args, **kwargs):
    liste_responsable = Responsable.objects.all()
    context = {
        'responsables' : liste_responsable,
        'nom_responsable' : 'Nom du responsable',
    }
    return render(request, 'responsables/indexResponsable.html', context)


class LoginResponsable(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'responsables/login.html')

    def post(self, request, *args, **kwargs):
        email = request.POST.get("email")
        mot_de_passe = request.POST.get("mot_de_passe")

        try:
            responsable = Responsable.objects.get(email=email)
        except Responsable.DoesNotExist:
            messages.error(request, "Email ou mot de passe incorrect.")
            return render(request, 'responsables/login.html')
        mot_de_passe_dechiffre = decrypt_password(responsable.mot_de_passe)

        if mot_de_passe.strip() == mot_de_passe_dechiffre.strip():
            request.session["responsable_id"] = responsable.id
            messages.success(request, f"Bienvenue {responsable.prenom_responsable} !")
            return redirect("personnes:carte")
        else:
            messages.error(request, "Email ou mot de passe incorrect.")
            return render(request, 'responsables/login.html')


class DeleteResponsable(View):
    def post(self, request, pk, *args, **kwargs):
        try: 
            responsable = Responsable.objects.get(pk=pk)
            responsable.delete()
            messages.success(request, 'Responsable supprimé avec succès')
        except Responsable.DoesNotExist:
            messages.error(request, 'Responsable introuvable')
        return redirect('responsables:indexResponsable')

class CreateResponsable(View):
    def get(self, request, *args, **kwargs):
        form = ResponsableForm()
        return render(request, 'responsables/create_responsable.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = ResponsableForm(request.POST, request.FILES)
        if form.is_valid():
            responsable = form.save(commit=False)
            responsable.mot_de_passe = encrypt_password(form.cleaned_data['mot_de_passe'])
            responsable.save()
            messages.success(request, 'Responsable enregistré avec succès')
            return redirect('responsables:indexResponsable')
        else:
            messages.error(request, 'Erreur lors de l\'enregistrement du responsable')
            return render(request, 'responsables/create_responsable.html', {'form': form})
class UpdateResponsable(View):
    def get(self, request, pk, *args, **kwargs):
        responsable = Responsable.objects.get(pk=pk)
        form = ResponsableForm(instance=responsable)
        #form.fields['arrondissement'].disabled = True
        return render(request, 'responsables/responsableUpdate.html', {'form': form})

    def post(self, request, pk, *args, **kwargs):
        responsable = Responsable.objects.get(pk=pk)
        form = ResponsableForm(request.POST, request.FILES, instance=responsable)
        #form.fields['arrondissement'].disabled = True 

        if form.is_valid():
            responsable = form.save(commit=False)
            responsable.mot_de_passe = encrypt_password(form.cleaned_data['mot_de_passe'])
            responsable.save()
            #form.save()
            messages.success(request, 'Responsable bien modifiée avec succès')
            return redirect('responsables:indexResponsable') 
        else:
            return render(request, 'responsables/responsableUpdate.html', {'form': form})


class ParametreResponsable(View):
    def get(self, request, pk, *args, **kwargs):
        if request.session.get('responsable_id') != pk:
            messages.error(request, "Accès non autorisé.")
            return redirect('personnes:indexPersonne')

        responsable = Responsable.objects.get(pk=pk)
        form = ResponsableForm(instance=responsable)
        form.fields['arrondissement'].disabled = True
        return render(request, 'responsables/parametres.html', {'form': form})

    def post(self, request, pk, *args, **kwargs):
        if request.session.get('responsable_id') != pk:
            messages.error(request, "Accès non autorisé.")
            return redirect('personnes:carte')

        responsable = Responsable.objects.get(pk=pk)
        form = ResponsableForm(request.POST, request.FILES, instance=responsable)

        form.fields['arrondissement'].disabled = True 

        if form.is_valid():
            responsable_modifie = form.save(commit=False)
            responsable_modifie.arrondissement = responsable.arrondissement
            responsable_modifie.mot_de_passe = encrypt_password(form.cleaned_data['mot_de_passe'])
            responsable_modifie.save()

            messages.success(request, 'Enregistré')
            return redirect('personnes:carte')
        else:
            return render(request, 'responsables/parametres.html', {'form': form})

class SeConnecter(View):
    def get(self, request, *args, **kwargs):
        arrondissements = Arrondissement.objects.all()
        return render(request, 'responsables/login.html', {
            'arrondissements': arrondissements
        })

    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        mot_de_passe = request.POST.get('mot_de_passe')

        responsable = Responsable.objects.filter(
            email=email,
            mot_de_passe=mot_de_passe
        ).first()


        if responsable:
            request.session['responsable_id'] = responsable.id
            messages.success(request, 'Connexion réussie')
            return redirect('personnes:carte')
        else:
            messages.error(request, 'Identifiants incorrects')
            return redirect('responsables:login')
 

class Deconnexion(View):
    def get(self, request):
        request.session.flush()
        messages.success(request, 'Déconnexion réussie')
        return redirect('responsables:login')


def envoyer_email(request):
    responsable = None
    responsable_id = request.session.get('responsable_id')
    if responsable_id:
        responsable = Responsable.objects.filter(pk=responsable_id).first()

    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            to_email = form.cleaned_data['to_email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            body = f"Expéditeur : {responsable.nom_responsable} {responsable.prenom_responsable} <{responsable.email}>\n\n{message}"

            email = EmailMessage(
                subject=subject,
                body=body,
                to=[to_email]
            )
            """
            email = EmailMessage(
                subject=subject,
                body=message,
                from_email=responsable.email if responsable else None,
                to=[to_email]
            )
            """
            files = request.FILES.getlist('attachments')
            for f in files:
                email.attach(f.name, f.read(), f.content_type)

            try:
                email.send()
                messages.success(request, "Email envoyé avec succès")
            except Exception as e:
                messages.error(request, f"Erreur lors de l'envoi: {e}")

            return redirect('responsables:email_form')
    else:
        form = EmailForm()

    return render(request, 'responsables/email_form.html', {
        'form': form,
        'responsable': responsable,
    })


def toutes_notifications(request):
    if 'responsable_id' not in request.session:
        return redirect('responsables:connexion')

    responsable_id = request.session['responsable_id']
    notifications = Notification.objects.filter(destinataire_id=responsable_id).order_by('-date_creation')

    return render(request, 'responsables/notifications.html', {
        'notifications': notifications
    })

def marquer_notification_lue(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, destinataire=request.session.get('responsable_id'))
    notification.est_lue = True
    notification.save()

    if notification.url and notification.url != "#":
        return redirect(notification.url)
    else:
        return redirect('responsables:notifications')
    
def notifications_non_lues(request):
    if 'responsable_id' in request.session:
        responsable_id = request.session['responsable_id']
        non_lues = Notification.objects.filter(destinataire_id=responsable_id, est_lue=False)
        toutes = Notification.objects.filter(destinataire_id=responsable_id).order_by('-date_creation')
        return {
            'notifications_non_lues': non_lues.count(),
            'notifications_liste': toutes[:5] 
        }
    return {'notifications_non_lues': 0, 'notifications_liste': []}

def notifications_view(request):
    responsable_id = request.session.get('responsable_id')
    notifications = Notification.objects.filter(destinataire_id=responsable_id).order_by('-date_creation')
    return render(request, 'responsables/notifications.html', {'notifications': notifications})

from django.contrib import messages
from django.shortcuts import redirect

def supprimer_notifications(request):
    if request.method == "POST":
        ids = request.POST.getlist("notifications")  # récupère les IDs cochés
        if ids:
            Notification.objects.filter(id__in=ids, destinataire_id=request.session.get('responsable_id')).delete()
            messages.success(request, "Les notifications sélectionnées ont été supprimées.")
        else:
            messages.warning(request, "Aucune notification sélectionnée.")
    return redirect("responsables:notifications")
