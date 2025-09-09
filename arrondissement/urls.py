from django.urls import path
from .views import index, CreateArrondissement, UpdateArrondissement, DeleteArrondissement

app_name = 'arrondissements'

urlpatterns = [
    path('', index, name='indexArrondissement'),
    path('create-arrondissement/', CreateArrondissement.as_view(), name='create_arrondissement'),
    path('arrondissementUpdate/<int:pk>', UpdateArrondissement.as_view(), name='arrondissementUpdate'),
    path('arrondissementDelete/<int:pk>', DeleteArrondissement.as_view(), name='deleteArrondissement'),
    

]