from django.shortcuts import render
from django.http import HttpResponse, QueryDict, HttpResponseRedirect
from django.views import View
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from prueba1.exceptions import UnallowedUserException
from prueba1.forms.oferta_forms import OfertaCreacionForm, OfertaEdicionForm, OfertaVetoForm
from prueba1.models.oferta_models import Oferta
from prueba1.models.perfil_models import Usuario
from prueba1.services.oferta_services import crea_oferta, edita_oferta, elimina_oferta, veta_oferta, \
    levanta_veto_oferta, oferta_formulario, lista_ofertas, cierra_oferta


class ListadoOfertaView(View):
    # No se requieren permisos para visitar esta pagina
    template_name = 'oferta/listado_ofertas.html'

    def get(self, request):
        context = {}
        # Se obtienen todas las oferta
        oferta = Oferta.objects.all()
        # Se consulta que usuario esta autenticado en este momento
        try:
            usuario = Usuario.objects.get(django_user_id = request.user.id)
        except ObjectDoesNotExist:
            usuario = None
        # Se añaden al contexto las oferta y el usuario y se muestra el listado
        context.update({'ofertas': lista_ofertas(request), 'usuario': usuario})
        return render(request, self.template_name, context)

class CreacionOfertaView(LoginRequiredMixin, View):
    # Todas las comprobaciones de permisos de esta vista las realiza el LoginRequiredMixin
    template_name = 'oferta/creacion_ofertas.html'

    def get(self, request):
        context = {}
        # Se genera el formulario vacio de la oferta a crear
        form = OfertaCreacionForm()
        # Se mete el formulario en el contexto y las variables para el estilo de validacion
        # ademas de mostrar el formulario
        context.update({
            'form': form, 
            'validated': False, 
            'form_class': 'needs-validation'
        })
        return render(request, self.template_name, context)

    def post(self, request):
        context = {}
        # Se crea un objeto formulario con los paramentros de entrada dados
        form = OfertaCreacionForm(request.POST)
        # Si el formulario es valido, se trata el formulario y se crea la oferta
        if form.is_valid():
            # Se valida el formulario con mas detalle
            form.clean()
            form_data = form.cleaned_data
            # Se inserta el campo autor en el diccionario que representa el formulario
            autor = Usuario.objects.get(django_user_id = request.user.id)
            form_data.update({'autor': autor})
            # Se intenta crear la oferta
            try:
                oferta_creada = crea_oferta(form_data, request)
            # Si hay una excepcion al crear la oferta se permanece en el formulario 
            # y se incluye un mensaje de error
            except Exception as e:
                messages.error(request, 'Se ha producido un error al crear la oferta')
                # Se mete en el contexto el formulario y las variables para el estilo
                context.update({
                    'form': form, 
                    'validated': True, 
                    'form_class': 'was-validated'
                })
                # Se muestra el formulario de creación de la oferta
                return render(request, self.template_name, context)
            # Redirige al los detalles de la oferta con un mensaje de exito
            messages.success(request, 'Se ha creado la oferta con exito')
            return HttpResponseRedirect(reverse('oferta_detalles', kwargs = {'oferta_id': oferta_creada.id}))
        # Si el formulario no es valido
        else:
            # Vuelve al formulario cuando haya un error de validacion
            # Se valida el formulario con mas detalle
            form.clean()
            # Se da un mensaje de error 
            messages.error(request, 'Se ha producido un error al crear la oferta')
            # Se mete en el contexto el formulario y las variables para el estilo
            context.update({
                'form': form, 
                'validated': True, 
                'form_class': 'was-validated'
            })
            # Se muestra el formulario de la creacion de la oferta
            return render(request, self.template_name, context)

class EdicionOfertaView(LoginRequiredMixin, View):
    # Para visitar esta pagina se requiere estar autenticado y ser el autor de la
    # oferta
    # El LoginRequiredMixin comprueba que el usuario esta autenticado
    # Se debe comprobar de forma programatica que el usuario es el autor de la oferta
    template_name = 'oferta/edicion_ofertas.html'

    def get(self, request, oferta_id):
        context = {}
        # Se comprueba la que se puede editar la oferta
        res = comprueba_editar_oferta(request, oferta_id)
        # Si se ha devuelto una oferta, entoces se asigna a la variable correspondiente
        if isinstance(res, Oferta):
            oferta = res
        # Si se ha devuelto una redireccion, entonces se devuelve la redirección
        elif isinstance(res, HttpResponseRedirect):
            return res
        # Se comprueba que se puede editar la oferta
        oferta = comprueba_editar_oferta(request, oferta_id)
        # Se genera un formulario en base a los datos de la oferta
        form = oferta_formulario(oferta)
        # Se mete el formulario y la variables de estilo en el contexto, aparte de 
        # la id de la oferta para el atributo action del formulario
        context.update({
            'oferta_id': oferta_id, 
            'form': form, 
            'validated': False, 
            'form_class': 'needs-validation'
        })
        # Se muestra el formulario de edición de la oferta
        return render(request, self.template_name, context)

    def post(self, request, oferta_id):
        context = {}
        # Se comprueba la que se puede editar la oferta
        res = comprueba_editar_oferta(request, oferta_id)
        # Si se ha devuelto una oferta, entoces se asigna a la variable correspondiente
        if isinstance(res, Oferta):
            oferta = res
        # Si se ha devuelto una redireccion, entonces se devuelve la redirección
        elif isinstance(res, HttpResponseRedirect):
            return res
        # Se crea un objeto formualrio en base a los datos recibidos
        form = OfertaEdicionForm(request.POST)
        # Si el formulario es valido, se trata el formulario y se edita la oferta
        if form.is_valid():
            # Se trata el formulario con más detalle
            form.clean()
            form_data = form.cleaned_data
            # Se prueba a editar la oferta
            try:
                edita_oferta(request, form_data, oferta)
            # En caso de excepción, se permanece en el formulario
            except Exception as e:
                # Se da un mensaje de error
                messages.error(request, 'Se ha producido un error al editar la oferta')
                # Se meten en el contexto el formulario, las variables para el estilo de 
                # la validación y la id de la oferta para el atributo action del formulario
                context.update({
                    'oferta_id': oferta_id, 
                    'form': form, 
                    'validated': True, 
                    'form_class': 'was-validated'
                })
                # Se muestra el formulario de edicion de la oferta
                return render(request, self.template_name, context)
            # Si no sucede ningun error, se redirige a los detalles de la oferta
            # junto con un mensaje de exito
            messages.success(request, 'Se ha editado la oferta con exito')
            return HttpResponseRedirect(reverse('oferta_detalles', kwargs = {'oferta_id': oferta.id}))
        # Si el formulario no es valido
        else:
            # Se valida el formulario con mas detalle
            form.clean()
            # Se da un mensaje de error
            messages.error(request, 'Se ha producido un error al editar la oferta')
            # Se inserta en el contexto el formulario, las variables para el estilo de la 
            # validacion y el id de la oferta para el atributo action del formulario
            context.update({
                'oferta_id': oferta_id, 
                'form': form, 
                'validated': True, 
                'form_class': 'was-validated'
            })
            # Se muestra el formulario de edición al usuario
            return render(request, self.template_name, context)

class EliminacionOfertaView(LoginRequiredMixin, View):
    # Para visitar esta pagina se requiere estar autenticado y ser el autor de la
    # oferta
    # El LoginRequiredMixin comprueba que el usuario esta autenticado
    # Se debe comprobar de forma programatica que el usuario es el autor de la oferta
    template_name = 'oferta/listado_ofertas.html'

    def get(self, request, oferta_id):
        context = {}
        # Se comprueba que se puede eliminar la oferta
        res = comprueba_eliminar_oferta(request, oferta_id)
        # Si devuelve una oferta, entonces se almacena en la vaariable correspondiente
        if isinstance(res, Oferta):
            oferta = res
        # Si devuelve una redirección, entonces se aplica dicha redirección
        elif isinstance(res, HttpResponseRedirect):
            return res
        # Se intenta eliminar la oferta
        try:
            elimina_oferta(request, oferta)
        # Si hay cualquier excepción, se redirige al usuario los detalles de la oferta
        # y se da un mensaje de error
        except Exception as e:
            messages.error(request, 'Se ha producido un error al eliminar la oferta')
            return HttpResponseRedirect(reverse('oferta_detalles', kwargs = {'oferta_id': oferta_id}))
        # Si se elimina la oferta correctamente se redirige al usuario al listado de 
        # mensajes y se muestra un mensaje de éxito
        messages.success(request, 'Se ha eliminado la oferta con exito')
        return HttpResponseRedirect(reverse('oferta_listado'))        

class DetallesOfertaView(View):
    # No se requiere estar autenticado para visitar esta página
    template_name = 'oferta/detalles_ofertas.html'

    def get(self, request, oferta_id):
        context = {}
        # Se obtiene el usuario autenticado
        try:
            usuario = Usuario.objects.get(django_user_id = request.user.id)
        except ObjectDoesNotExist as e:
            usuario = None
        # Se busca la oferta
        try:
            oferta = Oferta.objects.get(pk=oferta_id)
        # En caso de que no se encuentre la oferta, se redirige al usuario al
        # listado de oferta
        except ObjectDoesNotExist as e:
            return oferta_no_hallada(request)
        # Se añaden al contexto la oferta y el usuario
        context.update({
            'oferta': oferta,
            'usuario': usuario,
            'actividades': oferta.actividades.all(),
        })
        # Se muestra la vista de detalles
        return render(request, self.template_name, context)

class VetoOfertaView(UserPassesTestMixin, View):
    # El usuario debe estar autenticado y ser un administrador, se usará el
    # UserPassesTestMixin pra comprobar ambos
    template_name = 'oferta/veto_ofertas.html'
    permission_denied_message = 'No se tienen los permisos necesarios para vetar oferta'

    # Se comprueba que el usuario es un administrador
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        usuario = Usuario.objects.get(django_user = self.request.user)
        return usuario.es_admin

    def get(self, request, oferta_id):
        context = {}
        # Se comprueba que se puede vetar la oferta
        res = comprueba_vetar_oferta(request, oferta_id)
        # Si el resultado es una oferta, se almacena en la variable correspondiente
        if isinstance(res, Oferta):
            oferta = res
        # Si el resultado es una redirección, entonces se aplica la redirección
        elif isinstance(res, HttpResponseRedirect):
            return res
        # Se crea un formulario vacío para el veto de oferta
        form = OfertaVetoForm()
        # Se inserta en el contexto el formulario, las variables para el estilo de 
        # validación y el id de la oferta para el atributo action del formulario
        context.update({
            'oferta_id': oferta_id, 
            'form': form, 
            'validated': False, 
            'form_class': 'needs-validation'
        })
        # Se muestra el formulario de veto de oferta
        return render(request, self.template_name, context)
        
    def post(self, request, oferta_id):
        context = {}
        # Se comprueba que se puede vetar la oferta
        res = comprueba_vetar_oferta(request, oferta_id)
        # Si el resultado es una oferta, se almacena en la variable correspondiente
        if isinstance(res, Oferta):
            oferta = res
        # Si el resultado es una redirección, entonces se aplica la redirección
        elif isinstance(res, HttpResponseRedirect):
            return res
        # Se genera un formulario con los datos introducidos
        form = OfertaVetoForm(request.POST)
        # Si el formulario es válido
        if form.is_valid():
            # Se realiza una validación con más detalle
            form.clean()
            form_data = form.cleaned_data
            # Trata de vetar la oferta
            try:
                veta_oferta(request, form_data, oferta)
            # En cualquier otro caso, se permanece en el formulario y se incluye un 
            # mensaje de error
            except Exception as e:                    
                messages.error(request, 'Se ha producido un error al vetar la oferta')
                # Se introduce en el contexto el formulario, las variables para el estilo
                # de la validación y el id de la oferta para el atributo action del 
                # formulario
                context.update({
                    'oferta_id': oferta_id, 
                    'form': form, 
                    'validated': True, 
                    'form_class': 'was-validated'
                })
                # Se muestra el formulario de veto de la oferta
                return render(request, self.template_name, context)
            # Si se ha tenido éxito, se redirige al usuario a los detalles de la oferta
            # junto con un mensaje de éxito
            messages.success(request, 'Se ha vetado la oferta con exito')
            return HttpResponseRedirect(reverse('oferta_detalles', kwargs = {'oferta_id': oferta_id}))
        # Si el formulario no es valido
        else:
            # Se realiza una validación con más detalle
            form.clean()
            # Se muestra un mensaje de error
            messages.error(request, 'Se ha producido un error al vetar la oferta')
            # Se introduce en el contexto el formulario, las variables para el estilo de 
            # la validación y el id de la oferta para el atributo action del formulario
            context.update({
                'oferta_id': oferta_id, 
                'form': form, 
                'validated': True, 
                'form_class': 'was-validated',
            })
            # Se muestra el formulario de veto de la oferta
            return render(request, self.template_name, context)
            
class LevantamientoVetoOfertaView(UserPassesTestMixin, View):
    # El usuario debe estar autenticado y ser un administrador, se usará el
    # UserPassesTestMixin pra comprobar ambos
    template_name = 'oferta/listado_ofertas.html'
    permission_denied_message = 'No se tienen los permisos necesarios para levantar el veto sobre oferta'

    # Se comprueba que el usuario es un administrador
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        usuario = Usuario.objects.get(django_user = self.request.user)
        return usuario.es_admin

    def get(self, request, oferta_id):
        context = {}
        # Se comprueba que se puede levantar el veto sobre la oferta
        res = comprueba_levantar_veto_oferta(request, oferta_id)
        # Si el resultado es una oferta, entonces se almacena en la variable correspondiente
        if isinstance(res, Oferta):
            oferta = res
        # Si el resultado es una redirección, entonces se aplica la redirección
        elif isinstance(res, HttpResponseRedirect):
            return res
        # Se intenta levantar el veto sobre la oferta
        try:
            levanta_veto_oferta(request, oferta)
        # Si sucede alguna excepción, se redirige al usuario al listado de oferta con un mensaje de error
        except Exception as e:
            messages.error(request, 'No se poseen los permisos o requisitos necesarios para realizar esta accion')
            messages.error(request, e.args)
            return HttpResponseRedirect(reverse('oferta_detalles', kwargs = {'oferta_id': oferta_id}))
        # En caso de éxito, se redirige al usuario al listado de oferta con un mensaje de éxito
        messages.success(request, 'Se ha levantado el veto sobre la oferta con éxito')
        return HttpResponseRedirect(reverse('oferta_detalles', kwargs = {'oferta_id': oferta_id}))

class CierreOfertaView(LoginRequiredMixin, View):
    template_name = 'oferta/detalles_ofertas.html'

    def get(self, request, oferta_id):
        context = {}
        # Se comprueba que se puede cerrar la oferta
        res = comprueba_cerrar_oferta(request, oferta_id)
        # Si el resultado es una oferta, entonces se almacena en la variable correspondiente
        if isinstance(res, Oferta):
            oferta = res
        # Si el resultado es una redirección, entonces se aplica la redirección
        elif isinstance(res, HttpResponseRedirect):
            return res
        # Se intenta cerrar la oferta
        try:
            cierra_oferta(request, oferta)
        # Si sucede alguna excepción, se redirige al usuario a los detalles de la oferta con un mensaje de error
        except Exception as e:
            messages.error(request, 'No se poseen los permisos o requisitos necesarios para realizar esta accion')
            messages.error(request, e.args)
            return HttpResponseRedirect(reverse('oferta_detalles', kwargs = {'oferta_id': oferta_id}))
        # En caso de éxito, se redirige al usuario a los detalles de la oferta con un mensaje de éxito
        messages.success(request, 'Se ha cerrado la oferta con éxito')
        return HttpResponseRedirect(reverse('oferta_detalles', kwargs = {'oferta_id': oferta_id}))


#   Funciones utiles

def oferta_no_hallada(request):
    messages.error(request, 'No se ha encontrado la oferta')
    try:
        usuario = Usuario.objects.get(django_user_id = request.user.id)
    except ObjectDoesNotExist:
        usuario = None
    return HttpResponseRedirect(reverse('oferta_listado'))

def comprueba_editar_oferta(request, oferta_id):
    try:
        oferta = Oferta.objects.get(pk=oferta_id)
    # Si no existe la oferta, redirige al usuario al listado de oferta
    except ObjectDoesNotExist as e:
        return oferta_no_hallada(request)
    # Si la oferta no está en modo borrador, no se puede editar
    if not oferta.borrador:
        messages.error(request, 'No se puede editar una oferta que no está en modo borrador')
        return HttpResponseRedirect(reverse('oferta_detalles', kwargs={'oferta_id': oferta_id}))
    # No se puede editar una oferta cerrada
    if oferta.cerrada:
        messages.error(request, 'No se puede editar una oferta cerrada')
        return HttpResponseRedirect(reverse('oferta_detalles', kwargs={'oferta_id': oferta_id}))
    # No se puede editar una ofeta vetada
    if oferta.vetada:
        messages.error(request, 'No se puede editar una oferta vetada')
        return HttpResponseRedirect(reverse('oferta_detalles', kwargs={'oferta_id': oferta_id}))
    # Se comprueba que el usuario es el autor de la oferta
    # Si el usuario no es el autor de la oferta, se redirige al usuario a la
    # página de los detalles de la oferta con un mensaje de error
    if not request.user.id == oferta.autor.django_user.id:
        messages.error(request, 'No se poseen los permisos necesarios para editar la oferta')
        return HttpResponseRedirect(reverse('oferta_detalles', kwargs={'oferta_id': oferta_id}))
    # Se devuelve la oferta comprobada para poder usarla más adelante
    return oferta

def comprueba_eliminar_oferta(request, oferta_id):
    # Se comprueba que existe la oferta
    try:
        oferta = Oferta.objects.get(pk=oferta_id)
    # Si la oferta no existe, se redirige al usuario al listado de oferta
    except ObjectDoesNotExist as e:
        return oferta_no_hallada(request)
    # Si la oferta no está en modo borrador, no se puede eliminar
    if not oferta.borrador:
        messages.error(request, 'No se puede eliminar una oferta que no está en modo borrador')
        return HttpResponseRedirect(reverse('oferta_detalles', kwargs={'oferta_id': oferta_id}))
    # Si la oferta no está en modo borrador, no se puede eliminar
    if oferta.cerrada:
        messages.error(request, 'No se puede eliminar una oferta cerrada')
        return HttpResponseRedirect(reverse('oferta_detalles', kwargs={'oferta_id': oferta_id}))
    # Si la oferta no está en modo borrador, no se puede eliminar
    if oferta.vetada:
        messages.error(request, 'No se puede eliminar una oferta vetada')
        return HttpResponseRedirect(reverse('oferta_detalles', kwargs={'oferta_id': oferta_id}))
    # Se comprueba que el usuario es el autor de la oferta
    # Si el usuario no es el autor de la oferta, se redirige al usuario a la
    # página de los detalles de la oferta con un mensaje de error
    if not request.user.id == oferta.autor.django_user.id:
        messages.error(request, 'No se poseen los permisos necesarios para editar la oferta')
        return HttpResponseRedirect(reverse('oferta_detalles', kwargs={'oferta_id': oferta_id}))
    # Se devuelve la oferta para usarla más adelante
    return oferta

def comprueba_vetar_oferta(request, oferta_id):
    # Se comprueba que existe la oferta
    try:
        oferta = Oferta.objects.get(pk=oferta_id)
    # Si no existe se redirige al usuario al listado de oferta
    except ObjectDoesNotExist as e:
        return oferta_no_hallada(request)
    # Si la oferta está vetada no se puede vetar, por lo que se redirige al usuario a la vista de detalles
    if oferta.vetada:
        messages.error(request, 'No se puede vetar una oferta ya vetada')
        return HttpResponseRedirect(reverse('oferta_detalles', kwargs={'oferta_id': oferta_id}))
    # Si la oferta está en modo borrador, no se puede vetar
    if oferta.borrador:
        messages.error(request, 'No se puede vetar una oferta que está en modo borrador')
        return HttpResponseRedirect(reverse('oferta_detalles', kwargs={'oferta_id': oferta_id}))
    # Si la oferta está cerrada, no se puede vetar
    if oferta.cerrada:
        messages.error(request, 'No se puede vetar una oferta que está cerrada')
        return HttpResponseRedirect(reverse('oferta_detalles', kwargs={'oferta_id': oferta_id}))
    return oferta

def comprueba_levantar_veto_oferta(request, oferta_id):
    # Se trata de obtener la oferta
    try:
        oferta = Oferta.objects.get(pk=oferta_id)
    # Si no se encuentra la oferta se redirige al listado de oferta
    except ObjectDoesNotExist as e:
        return oferta_no_hallada(request)
    # Si la oferta no está vetada no se puede levantar el veto, por lo que se redirige al usuario a la vista de detalles
    if not oferta.vetada:
        messages.error(request, 'No se puede levantar el veto a una oferta sin vetar')
        return HttpResponseRedirect(reverse('oferta_detalles', kwargs={'oferta_id': oferta_id}))
    # Si la oferta está en modo borrador, no se puede levantar el veto
    if oferta.borrador:
        messages.error(request, 'No se puede levantar el veto a una oferta que está en modo borrador')
        return HttpResponseRedirect(reverse('oferta_detalles', kwargs={'oferta_id': oferta_id}))
    # Si la oferta está cerrada, entonces no se puede levantar el veto
    if oferta.cerrada:
        messages.error(request, 'No se puede levantar el veto a una oferta que está cerrada')
        return HttpResponseRedirect(reverse('oferta_detalles', kwargs={'oferta_id': oferta_id}))
    return oferta

def comprueba_cerrar_oferta(request, oferta_id):
    # Se trata de obtener la oferta
    try:
        oferta = Oferta.objects.get(pk=oferta_id)
    # Si no se encuentra la oferta se redirige al listado de oferta
    except ObjectDoesNotExist as e:
        return oferta_no_hallada(request)
    # Si la oferta está vetada no se puede cerrar, por lo que se redirige al usuario a la vista de detalles
    if oferta.vetada:
        messages.error(request, 'No se cerrar una oferta vetada')
        return HttpResponseRedirect(reverse('oferta_detalles', kwargs={'oferta_id': oferta_id}))
    # Si la oferta está en modo borrador, no se puede cerrar
    if oferta.borrador:
        messages.error(request, 'No se puede cerrar una oferta que está en modo borrador')
        return HttpResponseRedirect(reverse('oferta_detalles', kwargs={'oferta_id': oferta_id}))
    # Si la oferta está cerrada, entonces no se puede cerrar
    if oferta.cerrada:
        messages.error(request, 'No se puede cerrar una oferta que está cerrada')
        return HttpResponseRedirect(reverse('oferta_detalles', kwargs={'oferta_id': oferta_id}))
    return oferta