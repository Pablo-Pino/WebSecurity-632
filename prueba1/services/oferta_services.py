from django.contrib.auth.models import User
from django.db import transaction
from datetime import date
from random import choice
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from prueba1.models.oferta_models import Oferta
from prueba1.models.perfil_models import Usuario
from prueba1.forms.oferta_forms import OfertaEdicionForm
from prueba1.exceptions import UnallowedUserException
from prueba1.services.util_services import genera_identificador

@transaction.atomic
def lista_ofertas(request):
    if not request.user.is_authenticated:
        raise Exception('Se debe estar autenticado para listar las ofertas')
    usuario = Usuario.objects.get(django_user__id=request.user.id)
    if usuario.es_admin:
        return Oferta.objects.exclude((Q(cerrada=True) | Q(borrador=True)) & ~Q(autor=usuario))
    else:
        return Oferta.objects.exclude((Q(cerrada=True) | Q(borrador=True) | Q(vetada=True)) & ~Q(autor=usuario))

@transaction.atomic
def crea_oferta(oferta_dict, request):
    if not request.user.is_authenticated:
        raise Exception('Se debe estar autenticado para crear una oferta')
    oferta = Oferta(
        titulo = oferta_dict['titulo'],
        descripcion = oferta_dict['descripcion'],
        autor = oferta_dict['autor'],
        borrador = True,
        vetada = False,
        cerrada = False,
        fecha_creacion = date.today(),
        identificador = 'OFR-' + genera_identificador(),
    )
    oferta.full_clean()
    oferta.save()
    oferta.actividades.set(oferta_dict['actividades'])
    oferta.full_clean()
    oferta.save()
    return oferta

def oferta_formulario(oferta):
    data = {
        'titulo': oferta.titulo,
        'descripcion': oferta.descripcion,
        'borrador': oferta.borrador,
        'actividades': oferta.actividades,
    }
    form = OfertaEdicionForm(data)
    return form

@transaction.atomic
def edita_oferta(request, form_data, oferta):
    if not oferta.autor.django_user.id == request.user.id:
        raise UnallowedUserException()
    if not oferta.borrador:
        raise Exception('No se puede editar una oferta que no está en modo borrador')
    oferta.titulo = form_data['titulo']
    oferta.descripcion = form_data['descripcion']
    oferta.actividades.set(form_data['actividades'])
    oferta.borrador = form_data['borrador']
    oferta.full_clean()
    oferta.save(update_fields = ['titulo', 'descripcion', 'borrador'])
    return oferta

@transaction.atomic
def cierra_oferta(request, oferta):
    if not oferta.autor.django_user.id == request.user.id:
        raise UnallowedUserException()
    oferta.cerrada = True
    oferta.full_clean()
    oferta.save(update_fields = ['cerrada'])
    return oferta

@transaction.atomic
def elimina_oferta(request, oferta):
    if not oferta.autor.django_user.id == request.user.id:
        raise UnallowedUserException()
    if not oferta.borrador:
        raise Exception(['No se puede eliminar una oferta que no está en modo borrador'])
    oferta.delete()

@transaction.atomic
def veta_oferta(request, form_data, oferta):
    usuario = Usuario.objects.get(django_user_id = request.user.id)
    if not usuario.es_admin:
        raise Exception('Se requieren permisos de administrador para realizar esta accion')
    if oferta.vetada:
        raise Exception('No se puede volver a vetar una oferta vetada')
    oferta.motivo_veto = form_data['motivo_veto']
    oferta.vetada = True
    oferta.full_clean()
    oferta.save(update_fields = ['motivo_veto', 'vetada'])

@transaction.atomic
def levanta_veto_oferta(request, oferta):
    usuario = Usuario.objects.get(django_user_id = request.user.id)
    if not usuario.es_admin:
        raise Exception('Se requieren permisos de administrador para realizar esta accion')
    if not oferta.vetada:
        raise Exception('No se puede levantar el veto sobre una oferta no vetada')
    oferta.motivo_veto = None
    oferta.vetada = False
    oferta.full_clean()
    oferta.save(update_fields = ['motivo_veto', 'vetada'])
