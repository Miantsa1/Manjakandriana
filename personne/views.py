from django.shortcuts import render, redirect, HttpResponse, get_object_or_404, reverse
from .models import Personne
from personne.utils import ajouter_notification
from django.views import View
import io
import xlsxwriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from responsable.models import Responsable
from responsable.models import Notification
import base64
from io import BytesIO
from datetime import datetime
from django.views.generic import DetailView
from .forms import PersonneForm
from django.contrib import messages
import qrcode
from django.utils.dateparse import parse_date
from arrondissement.models import Arrondissement
from django.db.models import Count
from django.http import JsonResponse
from .mixins import RoleRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.shortcuts import render
from django.db.models import Q
from .models import Personne
from historique.models import HistoriqueAction


def index(request, *args, **kwargs):
    responsable_id = request.session.get('responsable_id')
    if responsable_id:
        responsable = Responsable.objects.get(pk=responsable_id)
        personnes_primata = Personne.objects.filter(est_valide=True, date_remplacement_cni__isnull=True)
        personnes_duplicata = Personne.objects.filter(est_valide=True, date_remplacement_cni__isnull=False)
    
    context = {
        'personnes_primata': personnes_primata,
        'personnes_duplicata': personnes_duplicata,
        'nom_personne': 'Nom de la personne',
    }
    return render(request, 'personnes/indexPersonne.html', context)

def get_responsable(request):
    responsable_id = request.session.get('responsable_id')
    if responsable_id:
        return Responsable.objects.get(pk=responsable_id)
    return None

def role_required(role):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            responsable_id = request.session.get('responsable_id')
            if not responsable_id:
                return redirect('login')

            responsable = Responsable.objects.get(pk=responsable_id)
            if responsable.fonction != role:
                return redirect('personnes:indexPersonne')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


class CreatePersonne(RoleRequiredMixin, View):
    allowed_roles = ["arrondissement"]

    def get(self, request, *args, **kwargs):
        form = PersonneForm()
        return render(request, 'personnes/create_personne.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = PersonneForm(request.POST, request.FILES)
        if form.is_valid():
            personne = form.save(commit=False)
            responsable_id = request.session.get('responsable_id')
            if responsable_id:
                personne.responsable_id = responsable_id
            personne.save()

            responsable_connecte = Responsable.objects.get(id=responsable_id)

            HistoriqueAction.objects.create(
                responsable=responsable_connecte,
                fonction=responsable_connecte.fonction,
                action='ajout',
                description=f"Ajout d'une nouvelle personne : {personne.nom_personne} {personne.prenom_personne}"
            )

            chefs_arr = Responsable.objects.filter(fonction="arrondissement").exclude(id=responsable_id)
            for chef in chefs_arr:
                ajouter_notification(
                    titre="Nouvelle personne ajoutée",
                    message=f"{responsable_connecte.nom_responsable} a ajouté une nouvelle personne.",
                    destinataire=chef
                )

            chefs_district = Responsable.objects.filter(fonction="district")
            for chef in chefs_district:
                ajouter_notification(
                    titre="Nouvelle personne ajoutée",
                    message=f"{responsable_connecte.nom_responsable} a ajouté une nouvelle personne.",
                    destinataire=chef
                )

            messages.success(request, 'Personne enregistrée avec succès')
            return redirect('personnes:valider_personne')
        else:
            messages.error(request, 'Erreur lors de l\'enregistrement du personne')
            return render(request, 'personnes/create_personne.html', {'form': form})



class DeletePersonne(RoleRequiredMixin, View):
    allowed_roles = ["arrondissement"]

    def post(self, request, pk, *args, **kwargs):
        try:
            personne = Personne.objects.get(pk=pk)
            responsable_id = request.session.get('responsable_id')
            responsable_connecte = Responsable.objects.get(pk=responsable_id)

            if responsable_id and personne.responsable_id != responsable_id:
                messages.error(request, 'Vous ne pouvez supprimer que vos propres enregistrements')
            else:
                HistoriqueAction.objects.create(
                    responsable=responsable_connecte,
                    fonction=responsable_connecte.fonction,
                    action='suppression',
                    description=f"Suppression de la personne : {personne.nom_personne} {personne.prenom_personne}"
                )
                personne.delete()
                messages.success(request, 'Personne supprimée avec succès')
        except Personne.DoesNotExist:
            messages.error(request, 'Personne introuvable')
        return redirect('personnes:indexPersonne')


class RecherchePersonneView(View):
    def get(self, request):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            query = request.GET.get('query', '')
            personnes = Personne.objects.filter(
                Q(nom_personne__icontains=query) |
                Q(prenom_personne__icontains=query) |
                Q(numero_cin__icontains=query)|
                Q(est_valide__icontains=query)
            ).values('id', 'nom_personne', 'prenom_personne','code_district', 'code_arrondissement', 'numero_sexe', 'numero_cin', 'est_valide')
            return JsonResponse(list(personnes), safe=False)
        return render(request, 'personnes/rechercher.html')

def valider_personne_list(request):
    responsable_id = request.session.get('responsable_id')
    if not responsable_id:
        return redirect('login')
    responsable = Responsable.objects.get(pk=responsable_id)
    if responsable.fonction == "arrondissement":
        personnes = Personne.objects.filter(est_valide=False, responsable_id=responsable_id)
    else:
        personnes = Personne.objects.filter(est_valide=False)

    return render(request, 'personnes/valider_personne.html', {'personnes': personnes, 'responsable': responsable})


def liste_personne_valide(request):
    responsable_id = request.session.get('responsable_id')
    personnes = Personne.objects.filter(est_valide=True)
    if responsable_id:
        personnes = personnes.filter(responsable_id=responsable_id)
    return render(request, 'personnes/liste_personne.html', {'personnes': personnes})


class ValiderPersonne(RoleRequiredMixin, View):
    allowed_roles = ["district"]

    def post(self, request, pk):
        personne = get_object_or_404(Personne, pk=pk)
        responsable_id = request.session.get('responsable_id')
        responsable_connecte = Responsable.objects.get(pk=responsable_id)
        action = request.POST.get('action')

        if action == "valider":
            personne.est_valide = True
            historique_action = "validation"
            historique_desc = f"Validation de la personne : {personne.nom_personne} {personne.prenom_personne}"
        elif action == "non_valider":
            personne.est_valide = False
            historique_action = "modification"
            historique_desc = f"Refus de validation de la personne : {personne.nom_personne} {personne.prenom_personne}"
        
        personne.save()

        HistoriqueAction.objects.create(
            responsable=responsable_connecte,
            fonction=responsable_connecte.fonction,
            action=historique_action,
            description=historique_desc
        )
        if personne.responsable:
            ajouter_notification(
                titre="Personne validée",
                message=f"La personne ajoutée par vous a été validée." if action == "valider" else f"La personne ajoutée par vous n'a pas été validée.",
                destinataire=personne.responsable
            )
        messages.success(request, "Action effectuée avec succès.")
        return redirect('personnes:valider_personne')


class UpdatePersonne(RoleRequiredMixin, View):
    allowed_roles = ["arrondissement"]
    def get(self, request, pk, *args, **kwargs):
        personne = Personne.objects.get(pk=pk)
        responsable_id = request.session.get('responsable_id')
        if responsable_id and personne.responsable_id != responsable_id:
            messages.error(request, 'Accès refusé')
            return redirect('personnes:liste_personne')
        form = PersonneForm(instance=personne)
        return render(request, 'personnes/personneUpdate.html', {'form': form})

    def post(self, request, pk, *args, **kwargs):
        personne = Personne.objects.get(pk=pk)
        responsable_id = request.session.get('responsable_id')
        responsable_connecte = Responsable.objects.get(pk=responsable_id)
        if responsable_id and personne.responsable_id != responsable_id:
            messages.error(request, 'Modification refusée')
            return redirect('personnes:liste_personne')
        form = PersonneForm(request.POST, request.FILES, instance=personne)
                
        HistoriqueAction.objects.create(
            responsable=responsable_connecte,
            fonction=responsable_connecte.fonction,
            action='modification',
            description=f"Modification du : {personne.nom_personne} {personne.prenom_personne}"
        
        )
        if form.is_valid():
            form.save()
            messages.success(request, 'Personne bien modifiée avec succès')
            return redirect('personnes:valider_personne')
        else:
            return render(request, 'personnes/personneUpdate.html', {'form': form})


def export_excel_personnes(request):
    output = io.BytesIO()
    fichier = xlsxwriter.Workbook(output, {'in_memory': True})
    sheet = fichier.add_worksheet("Personnes")
    bold = fichier.add_format({'bold': True, 'bg_color': '#D3D3D3', 'align': 'center'})

    headers = [
        'Nom', 'Prénom', 'Date de naissance', 'Lieu de naissance', 'Sexe',
        'Numéro CIN', 'Domicile', 'Arrondissement', 'Profession'
    ]

    for col_num, header in enumerate(headers):
        sheet.write(0, col_num, header, bold)

    personnes = Personne.objects.all()
    responsable_id = request.session.get('responsable_id')
    responsable = Responsable.objects.get(pk=responsable_id)
    if responsable.fonction == "arrondissement":
        personnes = Personne.objects.filter(est_valide=True, responsable_id=responsable_id)
    else:
        personnes = Personne.objects.filter(est_valide=True)
        
    for row_num, personne in enumerate(personnes, 1):
        sheet.write(row_num, 0, personne.nom_personne)
        sheet.write(row_num, 1, personne.prenom_personne)
        sheet.write(row_num, 2, str(personne.date_de_naissance))
        sheet.write(row_num, 3, personne.lieu_de_naissance)
        sheet.write(row_num, 4, personne.sexe)
        sheet.write(row_num, 5, personne.numero_cin)
        sheet.write(row_num, 6, personne.domicile)
        sheet.write(row_num, 7, str(personne.arrondissement))
        sheet.write(row_num, 8, personne.profession)

    fichier.close()
    output.seek(0)

    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="liste_personnes.xlsx"'
    return response


def export_pdf_personnes(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="liste_personnes.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    y = height - 2 * cm

    p.setFont("Helvetica-Bold", 16)
    p.drawString(2 * cm, y, "Liste des personnes enregistrées")
    y -= 2 * cm

    p.setFont("Helvetica-Bold", 10)
    headers = ['Nom', 'Prénom', 'Naissance', 'Lieu', 'Sexe', 'CIN', 'Arrond.', 'Profession']
    for col, header in enumerate(headers):
        p.drawString(2 * cm + col * 3 * cm, y, header)

    y -= 0.5 * cm
    p.setFont("Helvetica", 9)

    personnes = Personne.objects.all()
    responsable_id = request.session.get('responsable_id')
    responsable = Responsable.objects.get(pk=responsable_id)
    if responsable.fonction == "arrondissement":
        personnes = Personne.objects.filter(est_valide=True, responsable_id=responsable_id)
    else:
        personnes = Personne.objects.filter(est_valide=True)


    for personne in personnes:
        if y < 2 * cm:
            p.showPage()
            y = height - 2 * cm
            p.setFont("Helvetica", 9)
        p.drawString(2 * cm, y, personne.nom_personne)
        p.drawString(5 * cm, y, personne.prenom_personne)
        p.drawString(8 * cm, y, str(personne.date_de_naissance))
        p.drawString(11 * cm, y, personne.lieu_de_naissance)
        p.drawString(14 * cm, y, personne.sexe)
        p.drawString(16 * cm, y, personne.numero_cin)
        p.drawString(18.5 * cm, y, str(personne.arrondissement)[:10])
        p.drawString(21 * cm, y, personne.profession[:15])
        y -= 0.5 * cm

    p.save()
    return response

class DetailPersonneView(DetailView):
    model = Personne
    template_name = 'personnes/detail_personne.html'
    context_object_name = 'personne'

def detail_personne_qr(request, pk):
    personne = get_object_or_404(Personne, pk=pk)

    contenu = f"""
    Nom : {personne.nom_personne}
    Prénom : {personne.prenom_personne}
    Date de naissance : {personne.date_de_naissance}
    Lieu de naissance : {personne.lieu_de_naissance}
    Signe particulier : {personne.signe_particulier}
    CIN : {personne.code_district}{personne.code_arrondissement}{personne.numero_sexe}{personne.numero_cin}
    Sexe : {personne.sexe}
    Domicile : {personne.domicile}
    Arrondissement : {personne.arrondissement}
    Profession : {personne.profession}
    Père : {personne.pere}
    Mère : {personne.mere}
    """

    qr = qrcode.make(contenu)
    buffer = BytesIO()
    qr.save(buffer, format='PNG')
    image_qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render(request, 'personnes/detail_qr.html', {
        'personne': personne,
        'image_qr_base64': image_qr_base64
    })


def carte_madagascar(request):
    responsable = None
    if request.session.get('responsable_id'):
        responsable = Responsable.objects.get(id=request.session['responsable_id'])
    return render(request, 'carte.html', {'responsable': responsable})

def export_pdf_detail_personne(request, personne_id):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="fiche_de_renseignement.pdf"'

    personne = Personne.objects.get(id=personne_id)
    #buffer = BytesIO()
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    p.setFont("Helvetica", 9)
    numero_cni = f"{personne.code_district}{personne.code_arrondissement}{personne.numero_sexe}{personne.numero_cin}"
    for i, chiffre in enumerate(numero_cni):
        p.drawString(90 + i * 10, 794, chiffre)

    p.drawString(50, 782, personne.nom_personne)
    nouveauNom = personne.nouveau_nom_personne
    if nouveauNom == None:
        nouveauNom = f"  "
    else:
        nouveauNom = personne.nouveau_nom_personne
    p.drawString(20, 744, nouveauNom)

    prenoms = personne.prenom_personne.split()
    if len(prenoms) >= 1:
        p.drawString(60, 732, prenoms[0])
    if len(prenoms) > 1:
        p.drawString(20, 720, " ".join(prenoms[1:]))
    surnoms = personne.surnoms_personne
    if surnoms == None:
        surnoms = f"  "
    else:
        surnoms = personne.surnoms_personne
    p.drawString(100, 708, surnoms)
    p.drawString(50, 696, personne.date_de_naissance)
    p.drawString(30, 684, personne.lieu_de_naissance)

    nom_pere = personne.pere.split()
    if len(nom_pere) >= 1:
        p.drawString(60, 660, nom_pere[0])
    if len(nom_pere) > 1:
        p.drawString(20, 648, " ".join(nom_pere[1:]))

    nom_mere = personne.mere.split()
    if len(nom_mere) >= 1:
        p.drawString(60, 636, nom_mere[0])
    if len(nom_mere) > 1:
        p.drawString(20, 624, " ".join(nom_mere[1:]))



    p.drawString(260, 770, personne.profession)
    dom = f"Lot {personne.domicile}"
    p.drawString(260, 758, dom)
    commune = personne.commune_personne
    if commune == None:
        commune = f"  "
    else:
        commune = personne.commune_personne
    p.drawString(260, 732, commune)
    
    signe = personne.signe_particulier
    if signe == None:
        signe = f"  "
    else:
        signe = personne.signe_particulier
    p.drawString(260, 696, signe)
    p.drawString(260, 688, personne.taille_personne)
    p.drawString(260, 670, personne.origine)
    p.drawString(270, 650, personne.service_nationale)
    p.drawString(275, 640, personne.date_enregistrement_cin)
    remplacement = personne.date_remplacement_cni
    if remplacement == None:
        remplacement = f"  "
    else:
        remplacement = personne.date_remplacement_cni
    p.drawString(270, 624, remplacement)

    p.save()
    return response


class DashboardView(View):
    def get(self, request):
        responsable_id = request.session.get('responsable_id')
        responsable = Responsable.objects.get(pk=responsable_id)

        current_year = datetime.now().year
        annees = list(range(2020, current_year + 1))
        mois = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
        if responsable.fonction == "arrondissement":
            personnes = Personne.objects.filter(responsable_id=responsable_id, est_valide=True)
        else:
            personnes = Personne.objects.filter(est_valide=True)

        historiques = HistoriqueAction.objects.all().order_by('-date_action')
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')

        try:
            if start_date_str:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                personnes = personnes.filter(date_creation__gte=start_date)
                historiques = historiques.filter(date_action__date__gte=start_date)  # DateTimeField, -> __date
            if end_date_str:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
                personnes = personnes.filter(date_creation__lte=end_date)
                historiques = historiques.filter(date_action__date__lte=end_date)

        except ValueError:
            pass

        repartition_par_arr = (
            personnes.values('arrondissement__arrondissement_nom')
            .annotate(total=Count('id'))
        )

        context = {
            'total_personnes': personnes.count(),
            'total_responsables': Responsable.objects.count(),
            'total_arrondissements': Arrondissement.objects.count(),
            'repartition_par_arr': repartition_par_arr,
            'labels': [item['arrondissement__arrondissement_nom'] for item in repartition_par_arr],
            'data': [item['total'] for item in repartition_par_arr],
            'annees': annees,
            'mois': mois,
            'historiques': historiques,
            'start_date': start_date_str,
            'end_date': end_date_str,
        }
        return render(request, 'tableau_de_bord.html', context)


class DashboardDataView(View):
    def get(self, request):
        responsable_id = request.session.get('responsable_id')
        responsable = Responsable.objects.get(pk=responsable_id)

        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')

        if responsable.fonction == "arrondissement":
            personnes = Personne.objects.filter(responsable_id=responsable_id, est_valide=True)
        else:
            personnes = Personne.objects.filter(est_valide=True)

        historiques = HistoriqueAction.objects.all()
        try:
            if start_date_str:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                personnes = personnes.filter(date_creation__gte=start_date)
                historiques = historiques.filter(date_action__date__gte=start_date)
            if end_date_str:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
                personnes = personnes.filter(date_creation__lte=end_date)
                historiques = historiques.filter(date_action__date__lte=end_date)
        except ValueError:
            pass

        repartition = (
            personnes.values('arrondissement__arrondissement_nom')
            .annotate(total=Count('id'))
        )
        labels = [item['arrondissement__arrondissement_nom'] for item in repartition]
        data = [item['total'] for item in repartition]

        historiques = historiques.order_by('-date_action')[:5]
        show_all = request.GET.get("all", "0") == "1"
        if show_all:
            historiques = HistoriqueAction.objects.order_by("-date_action")

        historiques_list = [{
            "nom_responsable": h.responsable.nom_responsable,
            "fonction": h.fonction,
            "action": h.get_action_display(),
            "description": h.description,
            "date_action": h.date_action.strftime("%d/%m/%Y %H:%M")
        } for h in historiques]

        return JsonResponse({
            'labels': labels,
            'data': data,
            'total_personnes': personnes.count(),
            'total_arrondissements': Arrondissement.objects.count(),
            'total_responsables': Responsable.objects.count(),
            'historiques': historiques_list,
            "show_all": show_all
        })


@csrf_exempt
def exporter_pdf_cni_multi(request):
    if request.method == 'POST':
        ids = request.POST.getlist('personne_ids')[:4]
        personnes = Personne.objects.filter(id__in=ids, est_exporte_cni=False)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="CNI.pdf"'
        
        if not personnes.exists():
            messages.error(request, "Personne sélectionnée déjà exportée")
            return redirect('personnes:liste_personne')

        p = canvas.Canvas(response, pagesize=A4)
        width, height = A4

        for idx, personne in enumerate(personnes):
            offset = idx * 200

            p.setFont("Helvetica", 9)
            p.drawString(70, 794 - offset, personne.nom_personne)

            prenoms = personne.prenom_personne.split()
            if len(prenoms) >= 1:
                p.drawString(110, 763 - offset, prenoms[0])
            if len(prenoms) > 1:
                p.drawString(110, 749 - offset, " ".join(prenoms[1:]))

            p.drawString(130, 717 - offset, personne.date_de_naissance)
            p.drawString(150, 703 - offset, personne.lieu_de_naissance)
            p.drawString(130, 661 - offset, personne.taille_personne)

            numero_cni = f"{personne.code_district}{personne.code_arrondissement}{personne.numero_sexe}{personne.numero_cin}"
            for i, chiffre in enumerate(numero_cni):
                p.drawString(110 + i * 10, 633 - offset, chiffre)

            adresse = personne.domicile or ""
            adresse_parts = adresse.split()
            line1 = " ".join(adresse_parts[:5])
            line2 = " ".join(adresse_parts[5:]) if len(adresse_parts) > 5 else ""
            p.drawString(340, 820 - offset, line1)
            if line2:
                p.drawString(330, 806 - offset, line2)

            p.drawString(380, 792 - offset, str(personne.arrondissement))
            p.drawString(350, 778 - offset, str(personne.profession))
            p.drawString(360, 764 - offset, f"{personne.pere}")
            p.drawString(360, 750 - offset, f"{personne.mere}")
            p.drawString(380, 736 - offset, personne.lieu_enregistrement_cin)
            p.drawString(390, 722 - offset, personne.date_enregistrement_cin)

        p.save()
        personnes.update(est_exporte_cni=True)

        return response

    return redirect('personnes:indexPersonne')


def liste_personnesChoix(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    personnes_primata = Personne.objects.filter(type_cin='primata', est_valide=True)
    personnes_duplicata = Personne.objects.filter(type_cin='duplicata', est_valide=True)

    # Si dates fournies, filtrer
    if start_date and end_date:
        start = parse_date(start_date)
        end = parse_date(end_date)
        personnes_primata = personnes_primata.filter(date_creation__range=(start, end))
        personnes_duplicata = personnes_duplicata.filter(date_modification__range=(start, end))
    elif start_date:
        start = parse_date(start_date)
        personnes_primata = personnes_primata.filter(date_creation__gte=start)
        personnes_duplicata = personnes_duplicata.filter(date_modification__gte=start)
    elif end_date:
        end = parse_date(end_date)
        personnes_primata = personnes_primata.filter(date_creation__lte=end)
        personnes_duplicata = personnes_duplicata.filter(date_modification__lte=end)

    context = {
        'personnes_primata': personnes_primata.order_by('-date_creation'),
        'personnes_duplicata': personnes_duplicata.order_by('-date_modification'),
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'personnes/indexPersonne.html', context)



from django.shortcuts import render

import qrcode
import os
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from .models import Personne

from django.shortcuts import render, get_object_or_404
from .models import Personne


from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse
from .models import Personne
import io
import qrcode
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from django.templatetags.static import static

def cni_image(request, pk):
    personne = get_object_or_404(Personne, pk=pk)
    img = Image.new("RGB", (800, 500), color="white")
    draw = ImageDraw.Draw(img)
    try:
        fontK = ImageFont.truetype("arial.ttf", 20)
    except:
        fontK = ImageFont.load_default()

    photo_path = os.path.join(settings.BASE_DIR, "static/assets/img/logo_ministere.jpeg")
    photo1 = Image.open(photo_path).resize((60, 40))
    img.paste(photo1, (270, 2))
    
    draw.text((230, 45),  f"REPOBLIKAN ' I MADAGASIKARA", fill="black", font=fontK)
    draw.text((200, 60),  f"FITIAVANA - TANINDRAZANA - FANDROSOANA", fill="black", font=fontK)
    draw.text((230, 75),  f"KARAPANONDROM-PIRENENA", fill="black", font=fontK)
    draw.text((240, 90),  f"(Carte Nationale d'Identite)", fill="black", font=fontK)

    draw.text((30, 120),  f"ANARANA / Nom: {personne.nom_personne}", fill="black", font=fontK)
    draw.text((30, 150), f"FANAMPINY / Prenom: {personne.prenom_personne}", fill="black", font=fontK)
    draw.text((230, 170), f"TERAKA TAMIN'NY / Ne(e) le: {personne.date_de_naissance}", fill="black", font=fontK)
    draw.text((230, 200), f"TAO / a: {personne.lieu_de_naissance}", fill="black", font=fontK)
    draw.text((230, 230), f"FAMANTARANA MANOKANA / Signe particulier", fill="black", font=fontK)
    draw.text((230, 250), f"{personne.taille_personne}", fill="black", font=fontK)
    draw.text((230, 280), f"LAHARANA / N°: {personne.code_district}{personne.code_arrondissement}{personne.numero_sexe}{personne.numero_cin}", fill="black", font=fontK)
    
    draw.text((700, 20),  f"{personne.bon_de_commande}", fill="black", font=fontK)
    draw.text((500, 120),  f"FONENANA / Domicile: Lot {personne.domicile}", fill="black", font=fontK)
    draw.text((500, 150), f"BORIBORINTANY / Arrondissement: {personne.arrondissement}", fill="black", font=fontK)
    draw.text((500, 180), f"ASA ATAO / Profession: {personne.profession}", fill="black", font=fontK)
    draw.text((500, 210), f"RAY / pere: {personne.pere}", fill="black", font=fontK)
    draw.text((500, 240), f"RENY / mere:  {personne.mere}", fill="black", font=fontK)
    draw.text((500, 270), f"NATAO TAO / Fait   a  {personne.lieu_enregistrement_cin}", fill="black", font=fontK)
    draw.text((500, 290), f"TAMIN'NY / Le : {personne.date_enregistrement_cin}", fill="black", font=fontK)

    if personne.photo:
        photo_path1 = os.path.join(settings.MEDIA_ROOT, str(personne.photo))
        try:
            photo = Image.open(photo_path1).resize((170, 180))
            img.paste(photo, (30, 180)) 
        except Exception as e:
            print("Erreur photo:", e)
    
    url = f"http://10.232.136.77:8000/personne/{personne.pk}/cni/"
    qr_img = qrcode.make(url).resize((150, 150))
    img.paste(qr_img, (325, 340))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    return HttpResponse(buf.getvalue(), content_type="image/png")

import qrcode
import io
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Personne

def generate_qr(request, pk):
    personne = get_object_or_404(Personne, pk=pk)

    ip_locale = "10.232.136.77"  
    port = "8000"

    url = f"http://{ip_locale}:{port}/personne/{personne.pk}/cni/"

    qr_img = qrcode.make(url)
    buf = io.BytesIO()
    qr_img.save(buf, format="PNG")
    buf.seek(0)

    return HttpResponse(buf.getvalue(), content_type="image/png")
