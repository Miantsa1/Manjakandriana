from django.urls import path
from .views import index, CreateResponsable, DeleteResponsable, UpdateResponsable, envoyer_email, SeConnecter, Deconnexion, marquer_notification_lue, notifications_view, ParametreResponsable, LoginResponsable, supprimer_notifications
from . import views

app_name = 'responsables'

urlpatterns = [
    path('', index, name='indexResponsable'),
    path('logout/', Deconnexion.as_view(), name='logout'),
    #path('login', SeConnecter.as_view(), name='login'),
    path("login/", LoginResponsable.as_view(), name="login"),
    path('create-responsable/', CreateResponsable.as_view(), name='create_responsable'),
    path('responsableUpdate/<int:pk>', UpdateResponsable.as_view(), name='responsableUpdate'),
    path('responsableDelete/<int:pk>', DeleteResponsable.as_view(), name='deleteResponsable'),
    path('envoyer-email/', envoyer_email, name='email_form'),
    path('notification/<int:notification_id>/lue/', views.marquer_notification_lue, name='marquer_notification_lue'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/supprimer/', views.supprimer_notifications, name='supprimer_notifications'),
    path('parametre/<int:pk>', ParametreResponsable.as_view(), name='parametre'),
]

