# personne/mixins.py

from django.shortcuts import redirect
from django.contrib import messages
from responsable.models import Responsable

class RoleRequiredMixin:
    allowed_roles = []
    redirect_url = 'personnes:indexPersonne'

    def dispatch(self, request, *args, **kwargs):
        responsable_id = request.session.get('responsable_id')
        if not responsable_id:
            messages.error(request, "Veuillez vous connecter.")
            return redirect('login')

        responsable = Responsable.objects.get(pk=responsable_id)

        if responsable.fonction not in self.allowed_roles:
            messages.error(request, "Accès refusé : vous n'avez pas la permission.")
            return redirect(self.redirect_url)

        self.responsable = responsable
        return super().dispatch(request, *args, **kwargs)
