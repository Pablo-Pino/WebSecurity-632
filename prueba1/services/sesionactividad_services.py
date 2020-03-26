from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime

from prueba1.models.actividad_models import SesionActividad, Actividad
from prueba1.models.perfil_models import Usuario

@transaction.atomic
def crea_sesionactividad(request, actividad):
    usuario = Usuario.objects.get(django_user_id = request.user.id)
    try:
        sesionactividad = SesionActividad.objects.get(usuario = usuario, actividad = actividad)
        sesionactividad.token = usuario.django_user.username + str(datetime.now())
    except ObjectDoesNotExist as e:
        sesionactividad = SesionActividad(
            usuario = usuario,
            actividad = actividad,
            token = usuario.django_user.username + str(datetime.now())
        )
    sesionactividad.save()
    return sesionactividad

@transaction.atomic
def elimina_sesionactividad(request, actividad):
    token = request.data['token']
    sesionactividad = SesionActividad.objects.get(token = token, actividad = actividad)
    sesionactividad.delete()
