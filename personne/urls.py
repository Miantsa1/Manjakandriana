from django.urls import path
from .views import index, CreatePersonne, DeletePersonne, UpdatePersonne, export_excel_personnes, export_pdf_personnes, DetailPersonneView, export_pdf_detail_personne, carte_madagascar, DashboardView,  valider_personne_list, ValiderPersonne, liste_personne_valide, exporter_pdf_cni_multi, RecherchePersonneView, DashboardDataView, liste_personnesChoix, generate_qr, cni_image
from . import views

app_name = 'personnes'

urlpatterns = [
    path('', index, name='indexPersonne'),
    path('email', index, name='email'),
    path('carte/', views.carte_madagascar, name='carte'),
    path('create-personne/', CreatePersonne.as_view(), name='create_personne'),
    path('historique/', DashboardDataView.as_view(), name='dashboard_data'),
    path('personneUpdate/<int:pk>', UpdatePersonne.as_view(), name='personneUpdate'),
    path('personneDelete/<int:pk>', DeletePersonne.as_view(), name='deletePersonne'),
    path('export/excel/', export_excel_personnes, name='export_excel_personnes'),
    path('export/pdf/', export_pdf_personnes, name='export_pdf_personnes'),
    path('personne/<int:pk>/detail/', DetailPersonneView.as_view(), name='personne_detail_qr'),
    
    path('<int:pk>/qr/', views.detail_personne_qr, name='personne_detail_qr'), 
    path('personne/<int:personne_id>/pdf/', export_pdf_detail_personne, name='personne_pdf'),
    path('dashboard/', DashboardView.as_view(), name='tableau_de_bord'),
    path('valider/<int:pk>/', ValiderPersonne.as_view(), name='valider_une_personne'),
    path('valider-personne/', valider_personne_list, name='valider_personne'),
    path('liste-personnes-validees/', liste_personne_valide, name='liste_personne'),
    path('exporter-pdf-cni-multi/', views.exporter_pdf_cni_multi, name='exporter_pdf_cni_multi'),
    path('recherche/', RecherchePersonneView.as_view(), name='rechercher'),
    path('liste/', liste_personnesChoix, name='indexPersonne'),

    path("<int:pk>/generate-qr/", views.generate_qr, name="generate_qrr"),
    path("<int:pk>/cni/", views.cni_image, name="cni_image"),

]

