from django.core.paginator import Paginator
from django.shortcuts import render
from django.http import HttpResponse, QueryDict, HttpResponseRedirect
from django.views import View
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin

from WebSecurityApp.exceptions import UnallowedUserException
from WebSecurityApp.forms.perfil_forms import UsuarioForm,  AnexoForm
from WebSecurityApp.models.perfil_models import Usuario, Anexo
from WebSecurityApp.services.perfil_services import registra_usuario, usuario_formulario, edita_perfil, anexo_formulario, crea_anexo, edita_anexo, elimina_anexo
from WebSecurityServer.settings import numero_objetos_por_pagina


class RegistroUsuarioView(View):
    template_name = 'perfil/registro_usuario.html'
    
    def get(self, request):
        context = {}
        usuario_form = UsuarioForm()
        context.update({'usuario_form': usuario_form})
        return render(request, self.template_name, context)

    def post(self, request):
        context = {}
        usuario_form = UsuarioForm(request.POST)
        if usuario_form.is_valid():
            usuario_form.clean()
            usuario_form_data = usuario_form.cleaned_data
            registra_usuario(usuario_form_data)
            usuario_form = UsuarioForm()
            context.update({'usuario_form': usuario_form, 'registro_exito': True})
            return render(request, self.template_name, context)
        else:
            usuario_form.clean()
            context.update({'usuario_form': usuario_form, 'registro_exito': False})
            return render(request, self.template_name, context)

class DetallesPerfilView(View):
    template_name = 'perfil/detalles_perfil.html'

    def get(self, request):
        context = {}
        # Se busca el usuario
        try:
            usuario = Usuario.objects.get(django_user_id = request.user.id)
        # Si no se encuentra el usuario, se redirige a la pagina principal
        except ObjectDoesNotExist as e:
            messages.error(request, 'Se debe estar autenticado para acceder al perfil')
            return HttpResponseRedirect(reverse('home'))
        # Si se encuentra el usuario, se buscan sus anexos y se le muestra su perfil
        anexos = Anexo.objects.filter(usuario_id = usuario.id).order_by('id')
        # Se obtienen las actividades_realizadas por el usuario
        actividades_realizadas = usuario.actividades_realizadas.all().order_by('id')
        paginator = Paginator(actividades_realizadas, numero_objetos_por_pagina)
        page_number = request.GET.get('page')
        page_obj_actividades_realizadas = paginator.get_page(page_number)
        context.update({
            'usuario': usuario,
            'usuario_perfil': usuario,
            'anexos': anexos,
            'page_obj_actividades_realizadas': page_obj_actividades_realizadas,
        })
        return render(request, self.template_name, context)

class DetallesPerfilAjenoView(View):
    template_name = 'perfil/detalles_perfil.html'

    def get(self, request, usuario_id):
        context = {}
        # Se busca el usuario
        try:
            usuario = Usuario.objects.get(django_user_id = request.user.id)
        # Si no se encuentra el usuario, se redirige a la pagina principal
        except ObjectDoesNotExist as e:
            messages.error(request, 'Se debe estar autenticado para acceder al perfil de otro usuario')
            return HttpResponseRedirect(reverse('home'))
        try:
            usuario_perfil = Usuario.objects.get(pk=usuario_id)
        # Si no se enecuentra el usuario cuyo perfil se quiere ver, se redirige a la pagina principal
        except ObjectDoesNotExist as e:
            messages.error(request, 'No se ha encontrado el usuario')
            return HttpResponseRedirect(reverse('home'))
        # Si se encuentra el usuario, se buscan sus anexos y se le muestra su perfil
        anexos = Anexo.objects.filter(usuario_id = usuario_id).order_by('id')
        # Se obtienen las actividades_realizadas por el usuario que no estan vetadas
        actividades_realizadas = usuario_perfil.actividades_realizadas.filter(vetada=False).order_by('id')
        paginator = Paginator(actividades_realizadas, numero_objetos_por_pagina)
        page_number = request.GET.get('page')
        page_obj_actividades_realizadas = paginator.get_page(page_number)
        context.update({
            'usuario': usuario,
            'usuario_perfil': usuario_perfil,
            'anexos': anexos,
            'page_obj_actividades_realizadas': page_obj_actividades_realizadas,
        })
        return render(request, self.template_name, context)


class EdicionPerfilView(LoginRequiredMixin, View):
    template_name = 'perfil/edicion_perfil.html'

    def get(self, request):
        context = {}
        # Se busca el usuario
        try:
            usuario = Usuario.objects.get(django_user_id = request.user.id)
        # Si no se encuentra el usuario, se redirige a la pagina principal
        except ObjectDoesNotExist as e:
            messages.error(request, 'Se debe estar autenticado para acceder al perfil')
            return HttpResponseRedirect(reverse('home'))
        # Si se encuentra el usuario, se crea el formulario en base a sus datos
        form = usuario_formulario(usuario)
        context.update({
            'form': form,
            'validated': False, 
            'form_class': 'needs-validation'
        })
        return render(request, self.template_name, context)

    def post(self, request):
        context = {}
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.clean()
            form_data = form.cleaned_data
            # Se busca el usuario
            try:
                usuario = Usuario.objects.get(django_user_id = request.user.id)
            # Si no se encuentra el usuario, se redirige a la pagina principal
            except ObjectDoesNotExist as e:
                messages.error(request, 'Se debe estar autenticado para acceder al perfil')
                return HttpResponseRedirect(reverse('home'))
            # Si se encuentra el usuario, se trata el formulario
            try:
                edita_perfil(form_data, usuario)
            except Exception as e:
                messages.error(request, 'Ha habido un error al editar el perfil')
                messages.error(request, e.args[0])
                context.update({
                    'form': form,
                    'validated': True, 
                    'form_class': 'was-validated'
                })
                return render(request, self.template_name, context)
            messages.success(request, 'Se ha editado el perfil con exito')
            return HttpResponseRedirect(reverse('login'))
        else:
            form.clean()
            messages.error(request, 'Ha habido un error al editar el perfil')
            context.update({
                'form': form,
                'validated': True, 
                'form_class': 'was-validated'
            })
            return render(request, self.template_name, context)

class CreacionAnexoView(LoginRequiredMixin, View):
    template_name = 'perfil/formulario_anexo.html'

    def get(self, request):
        context = {}
        try:
            usuario = Usuario.objects.get(django_user_id = request.user.id)
        except ObjectDoesNotExist as e:
            messages.error(request, 'Se debe estar autenticado para acceder a la creacion de anexos')
            return HttpResponseRedirect(reverse('perfil_detalles'))
        form = AnexoForm()
        context.update({
            'form': form, 
            'validated': False, 
            'form_class': 'needs-validation'
        })
        return render(request, self.template_name, context)

    def post(self, request):
        context = {}
        form = AnexoForm(request.POST)
        if form.is_valid():
            # Trata los datos del formulario y crea la actividad
            form.clean()
            form_data = form.cleaned_data
            try:
                usuario = Usuario.objects.get(django_user_id = request.user.id)
            except ObjectDoesNotExist as e:
                messages.error(request, 'Se debe estar autenticado para acceder a la creacion de anexos')
                return HttpResponseRedirect(reverse('perfil_detalles'))
            try:
                crea_anexo(form_data, usuario)
            # El usuario no está permitido, por lo que se le redirige a los detalles del perfil
            except UnallowedUserException as e:
                messages.error(request, e.msg)
                return HttpResponseRedirect(reverse('perfil_detalles'))
            # Si no se encuentra el anexo se redirige al usuario a los detalles del perfil
            except ObjectDoesNotExist as e:
                messages.error(request, 'No se ha encontrado el anexo')
                return HttpResponseRedirect(reverse('perfil_detalles'))
            # En cualquier otro caso, se permanece en el formulario y se incluye un mensaje
            except Exception as e:
                messages.error(request, 'Se ha producido un error al crear el anexo')
                context.update({
                    'form': form, 
                    'validated': True, 
                    'form_class': 'was-validated'
                })
                return render(request, self.template_name, context)
            # Redirige a los detalles del perfil
            messages.success(request, 'Se ha creado el anexo con exito')
            return HttpResponseRedirect(reverse('perfil_detalles'))
        else:
            # Vuelve al formulario cuando haya un error de validacion
            form.clean()
            messages.error(request, 'Se ha producido un error al crear el anexo')
            context.update({
                'form': form, 
                'validated': True, 
                'form_class': 'was-validated'
            })
            return render(request, self.template_name, context)

class EdicionAnexoView(LoginRequiredMixin, View):
    template_name = 'perfil/formulario_anexo.html'

    def get(self, request, anexo_id):
        context = {}
        try:
            usuario = Usuario.objects.get(django_user_id = request.user.id)
        except ObjectDoesNotExist as e:
            messages.error(request, 'Se debe estar autenticado para acceder a la edicion de anexos')
            return HttpResponseRedirect(reverse('perfil_detalles'))
        try:
            anexo = Anexo.objects.get(pk=anexo_id)              
        except ObjectDoesNotExist as e:
            messages.error(request, 'No se ha encontrado el anexo')
            return HttpResponseRedirect(reverse('perfil_detalles'))
        if anexo.usuario != usuario:
            messages.error(request, 'No tienes los permisos o requisitos necesarios para realizar esta accion')
            return HttpResponseRedirect(reverse('perfil_detalles'))
        form = anexo_formulario(anexo)  
        context.update({
            'anexo_id': anexo_id, 
            'form': form, 
            'validated': False, 
            'form_class': 'needs-validation'
        })
        return render(request, self.template_name, context)

    def post(self, request, anexo_id):
        context = {}
        form = AnexoForm(request.POST)
        try:
            usuario = Usuario.objects.get(django_user_id = request.user.id)
        except ObjectDoesNotExist as e:
            messages.error(request, 'Se debe estar autenticado para acceder a la edicion de anexos')
            return HttpResponseRedirect(reverse('perfil_detalles'))
        try: 
            anexo = Anexo.objects.get(pk=anexo_id)
        # Si no se encuentra el anexo se redirige al usuario a los detalles del perfil
        except ObjectDoesNotExist as e:
            messages.error(request, 'No se ha encontrado el anexo')
            return HttpResponseRedirect(reverse('perfil_detalles'))
        if anexo.usuario != usuario:
            messages.error(request, 'No tienes los permisos o requisitos necesarios para realizar esta accion')
            return HttpResponseRedirect(reverse('perfil_detalles'))
        if form.is_valid():
            # Trata los datos del formulario y crea la actividad
            form.clean()
            form_data = form.cleaned_data
            try:
                edita_anexo(anexo, form_data, usuario)
            # El usuario no está permitido, por lo que se le redirige a los detalles del perfil
            except UnallowedUserException as e:
                messages.error(request, e.msg)
                return HttpResponseRedirect(reverse('perfil_detalles'))
            # En cualquier otro caso, se permanece en el formulario y se incluye un mensaje
            except Exception as e:
                messages.error(request, 'Se ha producido un error al editar el anexo')
                context.update({
                    'anexo_id': anexo_id,
                    'form': form, 
                    'validated': True, 
                    'form_class': 'was-validated'
                })
            # Redirige a los detalles del perfil
            messages.success(request, 'Se ha editado el anexo con exito')
            return HttpResponseRedirect(reverse('perfil_detalles'))
        else:
            # Vuelve al formulario cuando haya un error de validacion
            form.clean()
            messages.error(request, 'Se ha producido un error al editar el anexo')
            context.update({
                'form': form, 
                'validated': True, 
                'form_class': 'was-validated'
            })
            return render(request, self.template_name, context)

class EliminacionAnexoView(LoginRequiredMixin, View):
    template_name = 'perfil/detalles_perfil.html'

    def get(self, request, anexo_id):
        context = {}
        try:
            usuario = Usuario.objects.get(django_user_id = request.user.id)
        except ObjectDoesNotExist as e:
            messages.error(request, 'Se debe estar autenticado para acceder a la eliminacion de anexos')
            return HttpResponseRedirect(reverse('perfil_detalles'))
        # Se trata de hallar el anexo y eliminarlo
        try:
            anexo = Anexo.objects.get(pk=anexo_id)
            elimina_anexo(anexo, usuario)
        # Si el usuario no tiene permisos, se le redirige a los detalles del perfil
        except UnallowedUserException as e:
            messages.error(request, e.msg)
            return HttpResponseRedirect(reverse('perfil_detalles'))
        # Si no existe el anexo, se redirige al usuario a los detalles del perfil
        except ObjectDoesNotExist as e:
            messages.error(request, 'No se ha encontrado el anexo')
            return HttpResponseRedirect(reverse('perfil_detalles'))
        # Si hay cualquier otro error, se redirige al usuario a los detalles del perfil
        except Exception as e:
            messages.error(request, 'Se ha producido un error al eliminar el anexo')
            messages.error(request, e.args)
            return HttpResponseRedirect(reverse('perfil_detalles'))
        # Si se elimina el anexo correctamente se redirige al usuario a los detalles del perfil
        messages.success(request, 'Se ha eliminado el anexo con exito')
        return HttpResponseRedirect(reverse('perfil_detalles'))      

