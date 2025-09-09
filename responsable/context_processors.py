# responsable/context_processors.py
from .models import Notification
from .models import Responsable

def responsable_connecte(request):
    responsable_id = request.session.get('responsable_id')
    responsable = None
    if responsable_id:
        try:
            responsable = Responsable.objects.get(pk=responsable_id)
        except Responsable.DoesNotExist:
            pass
    return {'responsable': responsable}


def notifications_non_lues(request):
    if 'responsable_id' in request.session:
        responsable_id = request.session['responsable_id']
        count = Notification.objects.filter(destinataire_id=responsable_id, est_lue=False).count()
        return {'notifications_non_lues': count}
    return {'notifications_non_lues': 0}


def layout_context(request):
    notifications_liste = []
    notifications_non_lues = 0
    if 'responsable_id' in request.session:
        responsable_id = request.session['responsable_id']
        toutes = Notification.objects.filter(destinataire_id=responsable_id).order_by('-date_creation')
        non_lues = toutes.filter(est_lue=False)
        notifications_liste = toutes[:5]
        notifications_non_lues = non_lues.count()
    
    return {
        'notifications_liste': notifications_liste,
        'notifications_non_lues': notifications_non_lues
    }
