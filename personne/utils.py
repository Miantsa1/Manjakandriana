from responsable.models import Notification

def ajouter_notification(titre, message, destinataire, icone="bx bx-info-circle", url=None):
    Notification.objects.create(
        titre=titre,
        message=message,
        icone=icone,
        url=url or "",
        destinataire=destinataire
    )
