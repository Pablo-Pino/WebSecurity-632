from django.test import TestCase, RequestFactory, Client
from django.urls import reverse
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist

from datetime import date
import re

from prueba1.models.actividad_models import Actividad
from prueba1.models.oferta_models import Oferta
from prueba1.models.perfil_models import Usuario
from prueba1.models.oferta_models import Oferta
from prueba1.views.oferta_views import CreacionOfertaView

class OfertaTestCase(TestCase):
    
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        exec(open('populate_database.py').read())

    # Método que simula un login
    def login(self, username, password):
        response = self.client.post('/login/', {'username': username, 'password': password})
        usuario = Usuario.objects.get(django_user__username = username)
        return usuario

    # Método que simula un logout
    def logout(self):
        self.client.get('/logout/')

    # Un usuario accede al listado de ofertas correctamente
    def test_lista_ofertas(self):
        # Se inicializan variables y el usuario se loguea
        username = 'usuario1'
        password = 'usuario1'
        self.login(username, password)
        # Se crean variables con los datos correctos
        usuario_esperado = Usuario.objects.get(django_user__username = username)
        ofertas_esperadas = list(Oferta.objects.filter(Q(autor__django_user__username = username) |
                (Q(borrador = False) & Q(vetada=False) & Q(cerrada=False))).order_by('id'))
        # Se simula una petición al listado de la oferta
        response = self.client.get('/oferta/listado/')
        # Se obtienen los resultados
        usuario_recibido = response.context['usuario']
        ofertas_recibidas = list(response.context['ofertas'].order_by('id'))
        # Se comprueba que los resultados son correctos
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ofertas_esperadas, ofertas_recibidas)
        self.assertEqual(usuario_esperado, usuario_recibido)
        # El usuario se desloguea
        self.logout()

        # Un administrador accede al listado de ofertas correctamente
        def test_lista_ofertas_admin(self):
            # Se inicializan variables y el usuario se loguea
            username = 'usuario2'
            password = 'usuario2'
            self.login(username, password)
            # Se crean variables con los datos correctos
            usuario_esperado = Usuario.objects.get(django_user__username=username)
            ofertas_esperadas = list(Oferta.objects.filter(Q(autor__django_user__username=username) |
                    (Q(borrador=False) & Q(cerrada=False))).order_by('id'))
            # Se simula una petición al listado de la oferta
            response = self.client.get('/oferta/listado/')
            # Se obtienen los resultados
            usuario_recibido = response.context['usuario']
            ofertas_recibidas = list(response.context['ofertas'].order_by('id'))
            # Se comprueba que los resultados son correctos
            self.assertEqual(response.status_code, 200)
            self.assertEqual(ofertas_esperadas, ofertas_recibidas)
            self.assertEqual(usuario_esperado, usuario_recibido)
            # El usuario se desloguea
            self.logout()

    # Un usuario accede a los detalles de una oferta correctamente
    def test_detalles_oferta(self):
        # Se inicializan variables y se loguea el usuario
        username = 'usuario1'
        password = 'usuario1'
        self.login(username, password)
        # Se obtienen los datos esperados
        usuario_esperado = Usuario.objects.get(django_user__username = username)
        oferta_esperada = Oferta.objects.filter(Q(autor__django_user__username = username) & Q(borrador = True)).first()
        # Se simula que el usuario accede a los detalles de la oferta
        response = self.client.get('/oferta/detalles/{}/'.format(oferta_esperada.id))
        # Se obtienen los datos recibidos en la petición
        usuario_recibido = response.context['usuario']
        oferta_recibida = response.context['oferta']
        # Se comprueba que los datos son correctos
        self.assertEqual(response.status_code, 200)
        self.assertEqual(oferta_esperada, oferta_recibida)
        self.assertEqual(usuario_esperado, usuario_recibido)
        # El usuario se desloguea
        self.logout()

    # Un usuario accede a los detalles de una oferta que no existe
    def test_detalles_oferta_no_existe(self):
        # Se inicializan variables y se loguea el usuario
        username = 'usuario1'
        password = 'usuario1'
        id = 0
        self.login(username, password)
        # Se simula que el usuario accede a los detalles de la oferta
        response = self.client.get('/oferta/detalles/{}/'.format(id))
        # Se comprueba que los datos son correctos, el usuario es redirigido al listado al no poder hallarse
        # la oferta cuyos detalles se quieren ver
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/oferta/listado/')
        # El usuario se desloguea
        self.logout()

    # Un usuario crea una oferta correctamente
    def test_crea_oferta(self):
        # Se inicializan variables y se loguea el usuario
        username = 'usuario1'
        password = 'usuario1'
        usuario = self.login(username, password)
        # Se sacan las variables necesarias para comparar los datos
        numero_ofertas_antes = Oferta.objects.count()
        autor_esperado = Usuario.objects.get(django_user__username = 'usuario1')
        print('NIKO')
        # Se asignan variables para los datos de entrada
        titulo = 'test_crea'
        descripcion = 'test_crea'
        actividades = list(Actividad.objects.filter(borrador=False, vetada=False))[:2]
        actividades_post = []
        for actividad in actividades:
            actividades_post.append(actividad.id)
        # Se realiza la petición para crear la oferta
        response = self.client.post('/oferta/creacion/', {
            'titulo': titulo,
            'descripcion': descripcion,
            'actividades': actividades_post
        })
        print('NIKO')
        # Se obtienen las variables de salida
        numero_ofertas_despues = Oferta.objects.count()
        oferta_creada = Oferta.objects.all().order_by('id').last()
        # Se comparan los datos, se comprueba que el usuario es redirigido a la página de detalles de la oferta
        # tras crearla
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/oferta/detalles/{}/'.format(oferta_creada.id))
        self.assertEqual(numero_ofertas_antes, numero_ofertas_despues - 1)
        print('NII')
        # Se comprueba que los datos almacenados son los esperados
        self.assertEqual(oferta_creada.titulo, titulo)
        self.assertEqual(oferta_creada.descripcion, descripcion)
        self.assertEqual(list(oferta_creada.actividades.all()), actividades)
        self.assertFalse(oferta_creada.cerrada)
        self.assertTrue(oferta_creada.borrador)
        self.assertFalse(oferta_creada.vetada)
        self.assertIsNone(oferta_creada.motivo_veto)
        self.assertEqual(oferta_creada.fecha_creacion, date.today())
        self.assertEqual(oferta_creada.autor, usuario)
        # Se comprueba que el identificador de la oferta sigue el patrón indicado
        indentificador_regex = re.compile('^OFR-\w{10}$')
        self.assertEqual(indentificador_regex.match(oferta_creada.identificador) != None, True)
        # El usuario se desloguea
        self.logout()
        
    # Un usuario crea una oferta sin estar autenticado
    def test_crea_oferta_sin_loguear(self):
        # Se sacan las variables necesarias para comparar los datos
        numero_ofertas_antes = Oferta.objects.count()
        # Se asignan variables para los datos de entrada
        titulo = 'test_crea_sin_loguear'
        descripcion = 'test_crea_sin_loguear'
        actividades = list(Actividad.objects.filter(borrador=False, vetada=False))[:2]
        actividades_post = []
        for actividad in actividades:
            actividades_post.append(actividad.id)
        # Se realiza la petición para crear la oferta
        response = self.client.post('/oferta/creacion/', {
            'titulo': titulo, 
            'descripcion': descripcion,
            'actividades': actividades_post,
        })
        # Se obtienen las varibles de salida
        numero_ofertas_despues = Oferta.objects.count()
        # Se comparan los datos y se comprueba que no se ha creado la oferta, además de que el usuario ha sido
        # redirigido a la página de login al acceder a una página que requiere autenticación
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/oferta/creacion/')
        self.assertEqual(numero_ofertas_antes, numero_ofertas_despues)

    # Un usuario crea una oferta usando datos no válidos
    def test_crea_oferta_incorrecta(self):
        # Se inicializan variables y se loguea el usuario
        username = 'usuario1'
        password = 'usuario1'
        self.login(username, password)
        # Se sacan las variables necesarias para comparar los datos
        numero_ofertas_antes = Oferta.objects.count()
        # Se asignan variables para los datos de entrada
        titulo = ''
        descripcion = 'test_crea_incorrecta'
        actividades = list(Actividad.objects.filter(borrador=False, vetada=False))[:2]
        actividades_post = []
        for actividad in actividades:
            actividades_post.append(actividad.id)
        # Se realiza la petición para crear la oferta
        response = self.client.post('/oferta/creacion/', {
            'descripcion': descripcion,
            'actividades': actividades_post
        })
        # Se obtienen las varibles de salida
        numero_ofertas_despues = Oferta.objects.count()
        # Se comparan los datos y se comprueba que no se ha creado la oferta, se debe comprobar además que se ha
        # obtenido la página sin redirección y que se ha obtenido correctamente, debido a que se permanece en el 
        # formulario al suceder un error de validación
        self.assertEqual(response.status_code, 200)
        self.assertEqual(numero_ofertas_antes, numero_ofertas_despues)
        # Se desloguea el usuario
        self.logout()

    # Un usuario crea una oferta usando una actividad vetada
    def test_crea_oferta_actividad_vetada(self):
        # Se inicializan variables y se loguea el usuario
        username = 'usuario1'
        password = 'usuario1'
        self.login(username, password)
        # Se sacan las variables necesarias para comparar los datos
        numero_ofertas_antes = Oferta.objects.count()
        # Se asignan variables para los datos de entrada
        titulo = 'test_crea_vetada'
        descripcion = 'test_crea_vetada'
        actividades = list(Actividad.objects.filter(borrador=False, vetada=False))[:2]
        actividades_post = []
        for actividad in actividades:
            actividades_post.append(actividad.id)
        actividad_vetada = Actividad.objects.filter(vetada=True).first()
        actividades_post.append(actividad_vetada)
        # Se realiza la petición para crear la oferta
        response = self.client.post('/oferta/creacion/', {
            'titulo': titulo,
            'descripcion': descripcion,
            'actividades': actividades_post
        })
        # Se obtienen las varibles de salida
        numero_ofertas_despues = Oferta.objects.count()
        # Se comparan los datos y se comprueba que no se ha creado la oferta, se debe comprobar además que se ha
        # obtenido la página sin redirección y que se ha obtenido correctamente, debido a que se permanece en el
        # formulario al suceder un error de validación
        self.assertEqual(response.status_code, 200)
        self.assertEqual(numero_ofertas_antes, numero_ofertas_despues)
        # Se desloguea el usuario
        self.logout()

    # Un usuario crea una oferta usando una actividad en modo borrador
    def test_crea_oferta_actividad_borrador(self):
        # Se inicializan variables y se loguea el usuario
        username = 'usuario1'
        password = 'usuario1'
        self.login(username, password)
        # Se sacan las variables necesarias para comparar los datos
        numero_ofertas_antes = Oferta.objects.count()
        # Se asignan variables para los datos de entrada
        titulo = 'test_crea_vetada'
        descripcion = 'test_crea_vetada'
        actividades = list(Actividad.objects.filter(borrador=False, vetada=False))[:2]
        actividades_post = []
        for actividad in actividades:
            actividades_post.append(actividad.id)
        actividad_borrador = Actividad.objects.filter(borrador=True).first()
        actividades_post.append(actividad_borrador)
        # Se realiza la petición para crear la oferta
        response = self.client.post('/oferta/creacion/', {
            'titulo': titulo,
            'descripcion': descripcion,
            'actividades': actividades_post
        })
        # Se obtienen las varibles de salida
        numero_ofertas_despues = Oferta.objects.count()
        # Se comparan los datos y se comprueba que no se ha creado la oferta, se debe comprobar además que se ha
        # obtenido la página sin redirección y que se ha obtenido correctamente, debido a que se permanece en el
        # formulario al suceder un error de validación
        self.assertEqual(response.status_code, 200)
        self.assertEqual(numero_ofertas_antes, numero_ofertas_despues)
        # Se desloguea el usuario
        self.logout()

    '''
    
    # Un usuario edita una oferta correctamente
    def test_edita_oferta(self):
        # Se inicializan variables y se loguea el usuario
        username = 'usuario1'
        password = 'usuario1'
        oferta = Oferta.objects.filter(Q(autor__django_user__username = username) & Q(borrador = True)).first()
        self.login(username, password)
        # Se asignan variables para los datos de entrada
        titulo = 'test_edita'
        enlace = 'https://testedita.com/'
        descripcion = 'test_edita'
        comentable = True
        borrador = False
        # Se realiza la petición para editar la oferta
        response = self.client.post('/oferta/edicion/{}/'.format(oferta.id), {
            'titulo': titulo, 
            'enlace': enlace, 
            'descripcion': descripcion, 
            'comentable': comentable, 
            'borrador': borrador
        })
        # Se obtienen las varibles de salida
        oferta_editada = Oferta.objects.get(pk = oferta.id)
        # Se comparan los datos, se debe comprobar que el usuario ha sido redirigido a la página de detalles de la 
        # oferta tras ser editada
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/oferta/detalles/{}/'.format(oferta.id))
        # Se comprueba que los datos almacenados son los esperados
        self.assertEqual(oferta, oferta_editada)
        self.assertEqual(oferta_editada.titulo, titulo)
        self.assertURLEqual(oferta_editada.enlace, enlace)
        self.assertEqual(oferta_editada.descripcion, descripcion)
        self.assertEqual(oferta_editada.borrador, borrador)
        self.assertEqual(oferta_editada.vetada, False)
        self.assertEqual(oferta_editada.motivo_veto, None)
        self.assertEqual(oferta_editada.fecha_creacion, oferta.fecha_creacion)
        self.assertEqual(oferta_editada.comentable, comentable)
        self.assertEqual(oferta_editada.identificador, oferta.identificador)
        # El usuario se desloguea
        self.logout()

    # Un usuario edita un oferta sin estar autenticado
    def test_edita_oferta_sin_loguear(self):
        # Se inicializan variables y se loguea el usuario
        oferta = Oferta.objects.filter(borrador = True).first()
        # Se asignan variables para los datos de entrada
        titulo = 'test_edita_sin_loguear'
        enlace = 'https://testeditasinloguear.com/'
        descripcion = 'test_edita_sin_loguear'
        comentable = True
        borrador = False
        # Se realiza la petición para editar la oferta
        response = self.client.post('/oferta/edicion/{}/'.format(oferta.id), {
            'titulo': titulo, 
            'enlace': enlace, 
            'descripcion': descripcion, 
            'comentable': comentable, 
            'borrador': borrador
        })
        oferta_despues = Oferta.objects.get(pk = oferta.id)
        # Se comparan los datos, se debe comprobar que el usuario ha sido redirigido a la página de login, puesto a que 
        # ha accedido a una página que require autenticación sin estar autenticado
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/oferta/edicion/{}/'.format(oferta.id))
        # Se comprueba que no se ha editado ninguno de los campos editables
        self.assertEqual(oferta_despues.titulo, oferta.titulo)
        self.assertEqual(oferta_despues.descripcion, oferta.descripcion)
        self.assertURLEqual(oferta_despues.enlace, oferta.enlace)
        self.assertEqual(oferta_despues.borrador, oferta.borrador)
        self.assertEqual(oferta_despues.comentable, oferta.comentable)
        # El usuario se desloguea
        self.logout()

    # Un usuario edita una oferta que no es suya
    def test_edita_oferta_usuario_incorrecto(self):
        # Se inicializan variables y se loguea el usuario
        username = 'usuario2'
        password = 'usuario2'
        oferta = Oferta.objects.filter(borrador = True).exclude(autor__django_user__username = username).first()
        self.login(username, password)
        # Se asignan variables para los datos de entrada
        titulo = 'test_edita_incorrecto'
        enlace = 'https://testeditaincorrecto.com/'
        descripcion = 'test_edita_incorrecto'
        comentable = True
        borrador = False
        # Se realiza la petición para editar la oferta
        response = self.client.post('/oferta/edicion/{}/'.format(oferta.id), {
            'titulo': titulo, 
            'enlace': enlace, 
            'descripcion': descripcion, 
            'comentable': comentable, 
            'borrador': borrador
        })
        oferta_despues = Oferta.objects.get(pk = oferta.id)
        # Se comparan los datos y se comprueba que el usuario ha sido redirigido a la página de detalles de la 
        # oferta. Esto se debe a que no puede editar una oferta que no le pertenece.
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/oferta/detalles/{}/'.format(oferta.id))
        # Se comprueba que no se ha editado ninguno de los campos editables
        self.assertEqual(oferta_despues.titulo, oferta.titulo)
        self.assertEqual(oferta_despues.descripcion, oferta.descripcion)
        self.assertURLEqual(oferta_despues.enlace, oferta.enlace)
        self.assertEqual(oferta_despues.borrador, oferta.borrador)
        self.assertEqual(oferta_despues.comentable, oferta.comentable)
        # El usuario se desloguea
        self.logout()

    # Un usuario edita una oferta que no está en modo borrador
    def test_edita_oferta_no_borrador(self):
        # Se inicializan variables y se loguea el usuario
        username = 'usuario1'
        password = 'usuario1'
        oferta = Oferta.objects.filter(Q(borrador = False) & Q(autor__django_user__username = username)).first()
        self.login(username, password)
        # Se asignan variables para los datos de entrada
        titulo = 'test_edita_incorrecto'
        enlace = 'https://testeditaincorrecto.com/'
        descripcion = 'test_edita_incorrecto'
        comentable = True
        borrador = False
        # Se realiza la petición para editar la oferta
        response = self.client.post('/oferta/edicion/{}/'.format(oferta.id), {
            'titulo': titulo, 
            'enlace': enlace, 
            'descripcion': descripcion, 
            'comentable': comentable, 
            'borrador': borrador
        })
        oferta_despues = Oferta.objects.get(pk = oferta.id)
        # Se comparan los datos y se comprueba que el usuario ha sido redirigido a la página de detalles de la 
        # oferta. Esto se debe a que no puede editar una oferta que no está en modo borrador.
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/oferta/detalles/{}/'.format(oferta.id))
        # Se comprueba que no se ha editado nada
        self.assertEqual(oferta_despues.titulo, oferta.titulo)
        self.assertEqual(oferta_despues.descripcion, oferta.descripcion)
        self.assertURLEqual(oferta_despues.enlace, oferta.enlace)
        self.assertEqual(oferta_despues.borrador, oferta.borrador)
        self.assertEqual(oferta_despues.comentable, oferta.comentable)
        # El usuario se desloguea
        self.logout()

    # Un usuario edita una oferta usando datos no válidos
    def test_edita_oferta_incorrecta(self):
        # Se inicializan variables y se loguea el usuario
        username = 'usuario1'
        password = 'usuario1'
        oferta = Oferta.objects.filter(Q(borrador = True) & Q(autor__django_user__username = username)).first()
        self.login(username, password)
        # Se asignan variables para los datos de entrada
        titulo = 'test_edita_incorrecta'
        enlace = 'https://testedita_incorrecta.com/'
        descripcion = 'test_edita_incorrecta'
        comentable = True
        borrador = False
        # Se realiza la petición para editar la oferta
        response = self.client.post('/oferta/edicion/{}/'.format(oferta.id), {
            'titulo': titulo, 
            'enlace': enlace, 
            'descripcion': descripcion, 
            'comentable': comentable, 
            'borrador': borrador
        })
        oferta_despues = Oferta.objects.get(pk = oferta.id)
        # Se comparan los datos. Se comprueba que no ha sucedido ninguna redirección y que la página se ha obtenido
        # correctamente. Esto se debe a que al haber un error de validación el usuario permanece en el formulario.
        self.assertEqual(response.status_code, 200)
        # Se comprueba que no se ha editado nada
        self.assertEqual(oferta_despues.titulo, oferta.titulo)
        self.assertEqual(oferta_despues.descripcion, oferta.descripcion)
        self.assertURLEqual(oferta_despues.enlace, oferta.enlace)
        self.assertEqual(oferta_despues.borrador, oferta.borrador)
        self.assertEqual(oferta_despues.comentable, oferta.comentable)
        # El usuario se desloguea
        self.logout()

    # Un usuario elimina una oferta correctamente
    def test_elimina_oferta(self):
        # Se inicializan variables y se loguea el usuario
        username = 'usuario1'
        password = 'usuario1'
        oferta = Oferta.objects.filter(Q(autor__django_user__username = username) & Q(borrador = True)).first()
        numero_ofertas_antes = Oferta.objects.count()
        self.login(username, password)
        # Se realiza la petición para eliminar la oferta
        response = self.client.get('/oferta/eliminacion/{}/'.format(oferta.id))
        # Se obtienen las variables de salida. Se busca la oferta y se trata de capturar la excepción que se produce
        # cuando se busca una oferta que no existe. Si se captura la excepción, entonces se puede verificar que la 
        # oferta ha sido eliminada
        oferta_eliminada = False
        try:
            Oferta.objects.get(pk = oferta.id)
        except ObjectDoesNotExist as e:
            oferta_eliminada = True
        numero_ofertas_despues = Oferta.objects.count()
        # Se comparan los datos. Se comprueba que el usuario ha sido redirigido al listado de ofertas y que la
        # oferta ha sido eliminada
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/oferta/listado/')
        self.assertEqual(oferta_eliminada, True)
        self.assertEqual(numero_ofertas_antes, numero_ofertas_despues + 1)
        # El usuario se desloguea
        self.logout()

    # Un usuario elimina una oferta sin estar autenticado
    def test_elimina_oferta_sin_loguear(self):
        # Se inicializan variables
        oferta = Oferta.objects.filter(borrador = True).first()
        numero_ofertas_antes = Oferta.objects.count()
        # Se realiza la petición para eliminar la oferta
        response = self.client.get('/oferta/eliminacion/{}/'.format(oferta.id))
        # Se obtienen las variables de salida. Se busca la oferta y se trata de capturar la excepción que se produce
        # cuando se busca una oferta que no existe. Si se captura la excepción, entonces se puede verificar que la 
        # oferta ha sido eliminada
        oferta_eliminada = False
        try:
            Oferta.objects.get(pk = oferta.id)
        except ObjectDoesNotExist as e:
            oferta_eliminada = True
        numero_ofertas_despues = Oferta.objects.count()
        # Se comparan los datos. Se comprueba que el usuario, al tratar de acceder a una página que requiere 
        # autenticación sin estar autenticado, es redirigido a la página de login. Se comprueba además que no se ha 
        # eliminado la oferta
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/oferta/eliminacion/{}/'.format(oferta.id))
        self.assertEqual(oferta_eliminada, False)
        self.assertEqual(numero_ofertas_antes, numero_ofertas_despues)

    # Un usuario elimina una oferta que no es suya
    def test_elimina_oferta_usuario_incorrecto(self):
        # Se inicializan variables y se loguea el usuario
        username = 'usuario2'
        password = 'usuario2'
        oferta = Oferta.objects.exclude(autor__django_user__username = username).filter(borrador = True).first()
        numero_ofertas_antes = Oferta.objects.count()
        self.login(username, password)
        # Se realiza la petición para eliminar la oferta
        response = self.client.get('/oferta/eliminacion/{}/'.format(oferta.id))
        # Se obtienen las variables de salida. Se busca la oferta y se trata de capturar la excepción que se produce
        # cuando se busca una oferta que no existe. Si se captura la excepción, entonces se puede verificar que la 
        # oferta ha sido eliminada
        oferta_eliminada = False
        try:
            Oferta.objects.get(pk = oferta.id)
        except ObjectDoesNotExist as e:
            oferta_eliminada = True
        numero_ofertas_despues = Oferta.objects.count()
        # Se comparan los datos. Se comprueba que el usuario ha sido redirigido a los detalles de la oferta y que no
        # se ha eliminado la oferta. Esto se debe a que un usuario no puede eliminar una oferta que no le pertenece.
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/oferta/detalles/{}/'.format(oferta.id))
        self.assertEqual(numero_ofertas_antes, numero_ofertas_despues)
        self.assertEqual(oferta_eliminada, False)
        # El usuario se desloguea
        self.logout()

    # Un usuario elimina una oferta que no estaba en modo borrador
    def test_elimina_oferta_no_borrador(self):
        # Se inicializan variables y se loguea el usuario
        username = 'usuario1'
        password = 'usuario1'
        oferta = Oferta.objects.filter(Q(autor__django_user__username = username) & Q(borrador = False)).first()
        numero_ofertas_antes = Oferta.objects.count()
        self.login(username, password)
        # Se realiza la petición para crear la oferta
        response = self.client.get('/oferta/eliminacion/{}/'.format(oferta.id))
        # Se obtienen las variables de salida. Se busca la oferta y se trata de capturar la excepción que se produce
        # cuando se busca una oferta que no existe. Si se captura la excepción, entonces se puede verificar que la 
        # oferta ha sido eliminada
        oferta_eliminada = False
        try:
            Oferta.objects.get(pk = oferta.id)
        except ObjectDoesNotExist as e:
            oferta_eliminada = True
        numero_ofertas_despues = Oferta.objects.count()
        # Se comparan los datos
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/oferta/detalles/{}/'.format(oferta.id))
        self.assertEqual(numero_ofertas_antes, numero_ofertas_despues)
        self.assertEqual(oferta_eliminada, False)
        # El usuario se desloguea
        self.logout()
    
    # Un administrador veta una oferta
    def test_veta_oferta(self):
        # Se inicializan variables y se loguea el usuario
        username = 'usuario2'
        password = 'usuario2'
        oferta = Oferta.objects.filter(Q(vetada = False) & Q(borrador = False)).first()
        motivo_veto = 'Testing'
        self.login(username, password)
        # Se realiza la petición para vetar la oferta
        response = self.client.post('/oferta/veto/{}/'.format(oferta.id), {'motivo_veto': motivo_veto})
        # Se obtienen las variables de salida
        oferta_despues = Oferta.objects.get(pk = oferta.id)
        # Se comparan los datos. Se comprueba que el usuario ha sido redirigido a la paǵina de detalles y que la
        # oferta se ha vetado correctemente, además de guardarse el motivo de veto.
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/oferta/detalles/{}/'.format(oferta.id))
        self.assertEqual(oferta_despues.vetada, True)
        self.assertEqual(oferta_despues.motivo_veto, motivo_veto)
        # El usuario se desloguea
        self.logout()
    
    # Un usuario no autenticado veta una oferta
    def test_veta_oferta_sin_loguear(self):
        # Se inicializan variables y se loguea el usuario        
        oferta = Oferta.objects.filter(Q(vetada = False) & Q(borrador = False)).first()
        motivo_veto = 'Testing'
        # Se realiza la petición para vetar la oferta
        response = self.client.post('/oferta/veto/{}/'.format(oferta.id), {'motivo_veto': motivo_veto})
        # Se obtienen las variables de salida
        oferta_despues = Oferta.objects.get(pk = oferta.id)
        # Se comparan los datos. Se comprueba que la oferta no ha sufrido cambios y que el usuario ha sido redirigido
        # al login debido a que hay que esrar autenticado para vetar una oferta.
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/oferta/veto/{}/'.format(oferta.id))
        # Se comprueba que la oferta no ha sido vetada
        self.assertEqual(oferta_despues.vetada, False)
        self.assertEqual(oferta_despues.motivo_veto, None)
        # El usuario se desloguea
        self.logout()

    # Un usuario que no es administrador veta la oferta
    def test_veta_oferta_usuario_incorrecto(self):
        # Se inicializan variables y se loguea el usuario
        username = 'usuario1'
        password = 'usuario1'
        oferta = Oferta.objects.filter(Q(vetada = False) & Q(borrador = False)).first()
        motivo_veto = 'Testing'
        self.login(username, password)
        # Se realiza la petición para vetar la oferta
        response = self.client.post('/oferta/veto/{}/'.format(oferta.id), {'motivo_veto': motivo_veto})
        # Se obtienen las variables de salida
        oferta_despues = Oferta.objects.get(pk = oferta.id)
        # Se comparan los datos. Se comprueba que la oferta no ha sufrido cambios y que se ha producido un error 403
        # debido a que el usuario no tiene los permisos de administrador
        self.assertEqual(response.status_code, 403)
        self.assertEqual(oferta_despues.vetada, False)
        self.assertEqual(oferta_despues.motivo_veto, None)
        # El usuario se desloguea
        self.logout()

    # Un administrador veta una oferta ya vetada
    def test_veta_oferta_vetada(self):
        # Se inicializan variables y se loguea el usuario
        username = 'usuario2'
        password = 'usuario2'
        oferta = Oferta.objects.filter(Q(vetada = True) & Q(borrador = False)).first()
        motivo_veto = oferta.motivo_veto + 'Testing'
        self.login(username, password)
        # Se realiza la petición para vetar la oferta
        response = self.client.post('/oferta/veto/{}/'.format(oferta.id), {'motivo_veto': motivo_veto})
        # Se obtienen las variables de salida
        oferta_despues = Oferta.objects.get(pk = oferta.id)
        # Se comparan los datos. Se comprueba que la oferta no ha sufrido cambios y que el usuario ha sido redirigido
        # a los detalles de la oferta debido a que no se puede vetar una oferta ya vetada.
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/oferta/detalles/{}/'.format(oferta.id))
        self.assertEqual(oferta_despues.vetada, True)
        self.assertEqual(oferta_despues.motivo_veto, oferta.motivo_veto)
        # El usuario se desloguea
        self.logout()

    # Un administrador veta una oferta que ya existe
    def test_veta_oferta_inexistente(self):
        # Se inicializan variables y se loguea el usuario
        username = 'usuario2'
        password = 'usuario2'
        motivo_veto = 'Testing'
        self.login(username, password)
        # Se realiza la petición para vetar la oferta
        response = self.client.post('/oferta/veto/0/', {'motivo_veto': motivo_veto})
        # Se comparan los datos. El usuario es redirigido al listado de ofertas debido a que no se puede encontrar 
        # la oferta que se quiere vetar
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/oferta/listado/')
        # El usuario se desloguea
        self.logout()

    # Un adminsitrador veta una oferta insertando un motivo de veto no válido
    def test_veta_oferta_incorrecta(self):
        # Se inicializan variables y se loguea el usuario
        username = 'usuario2'
        password = 'usuario2'
        motivo_veto = 'Testing'
        oferta = Oferta.objects.filter(Q(vetada = False) & Q(borrador = False)).first()
        self.login(username, password)
        # Se realiza la petición para vetar la oferta
        response = self.client.post('/oferta/veto/{}/'.format(oferta.id))
        # Se obtienen las variables de salida
        oferta_despues = Oferta.objects.get(pk = oferta.id)
        # Se comparan los datos. Se comprueba que la oferta no ha sufrido cambios y que el usuario permanece el 
        # formulario de veto debido a que se ha insertado un motivo de veto no válido
        self.assertEqual(response.status_code, 200)
        self.assertEqual(oferta_despues.vetada, False)
        self.assertEqual(oferta_despues.motivo_veto, None)
        # El usuario se desloguea
        self.logout()

    # Un administrador veta una oferta que está en modo borrador
    def test_veta_oferta_borrador(self):
        # Se inicializan variables y se loguea el usuario
        username = 'usuario2'
        password = 'usuario2'
        motivo_veto = 'Testing'
        oferta = Oferta.objects.filter(Q(vetada = False) & Q(borrador = True)).first()
        self.login(username, password)
        # Se realiza la petición para vetar la oferta
        response = self.client.post('/oferta/veto/{}/'.format(oferta.id), {'motivo_veto': motivo_veto})
        # Se obtienen las variables de salida
        oferta_despues = Oferta.objects.get(pk = oferta.id)
        # Se comparan los datos. Se comprueba que la oferta no ha sufrido cambios y que el usuario ha sido
        # redirigido a los detalles de la oferta puesto a que no se puede vetar una oferta en modo borrador 
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('oferta_detalles', kwargs = {'oferta_id': oferta.id}))
        self.assertEqual(oferta_despues.vetada, False)
        self.assertEqual(oferta_despues.motivo_veto, None)
        # El usuario se desloguea
        self.logout()

    # Un administrador levanta el veto sobre una oferta
    def test_levanta_veto_oferta(self):
        # Se inicializan variables y se loguea el usuario
        username = 'usuario2'
        password = 'usuario2'
        oferta = Oferta.objects.filter(Q(vetada = True) & Q(borrador = False)).first()
        self.login(username, password)
        # Se realiza la petición para levantar el veto sobre la oferta
        response = self.client.get('/oferta/levantamiento_veto/{}/'.format(oferta.id))
        # Se obtienen las variables de salida
        oferta_despues = Oferta.objects.get(pk = oferta.id)
        # Se comparan los datos. Se comprueba que la oferta ya no está vetada y que no aparece el motivo de veto. Se
        # comprueba además que el usuario ha sido redirigido a los detalles de la oferta.
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/oferta/detalles/{}/'.format(oferta.id))
        self.assertEqual(oferta_despues.vetada, False)
        self.assertEqual(oferta_despues.motivo_veto, None)
        # El usuario se desloguea
        self.logout()

    # Un usuario levanta el veto sobre una oferta sin estar logueado
    def test_levanta_veto_oferta_sin_loguear(self):
        # Se inicializan variables y se loguea el usuario        
        oferta = Oferta.objects.filter(Q(vetada = True) & Q(borrador = False)).first()
        # Se realiza la petición para levantar el veto sobre la oferta
        response = self.client.get('/oferta/levantamiento_veto/{}/'.format(oferta.id))
        # Se obtienen las variables de salida
        oferta_despues = Oferta.objects.get(pk = oferta.id)
        # Se comparan los datos. Se comprueba que la oferta no ha sufrido cambios y que se ha redirigido al usuario al
        # login, puesto a que se require autenticación para levantar el veto sobre una oferta.
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/oferta/levantamiento_veto/{}/'.format(oferta.id))
        self.assertEqual(oferta_despues.vetada, True)
        self.assertEqual(oferta_despues.motivo_veto, oferta.motivo_veto)
        # El usuario se desloguea
        self.logout()

    # Un usuario levanta el veto sobre una oferta sin ser administrador
    def test_levanta_veto_oferta_usuario_incorrecto(self):
        # Se inicializan variables y se loguea el usuario
        username = 'usuario1'
        password = 'usuario1'
        oferta = Oferta.objects.filter(Q(vetada = True) & Q(borrador = False)).first()
        self.login(username, password)
        # Se realiza la petición para levantar el veto sobre la oferta
        response = self.client.get('/oferta/levantamiento_veto/{}/'.format(oferta.id))
        # Se obtienen las variables de salida
        oferta_despues = Oferta.objects.get(pk = oferta.id)
        # Se comparan los datos. Se comprueba que la oferta no ha sufrido cambios y que se ha producido un error 403
        # debido a que el usuario no tiene los permisos de administrador necesarios.
        self.assertEqual(response.status_code, 403)
        self.assertEqual(oferta_despues.vetada, True)
        self.assertEqual(oferta_despues.motivo_veto, oferta.motivo_veto)
        # El usuario se desloguea
        self.logout()

    # Un usuario levanta el veto sobre una oferta no vetada
    def test_levanta_veto_oferta_no_vetada(self):
        # Se inicializan variables y se loguea el usuario
        username = 'usuario2'
        password = 'usuario2'
        oferta = Oferta.objects.filter(Q(vetada = False) & Q(borrador = False)).first()
        self.login(username, password)
        # Se realiza la petición para levantar el veto sobre la oferta
        response = self.client.get('/oferta/levantamiento_veto/{}/'.format(oferta.id))
        # Se obtienen las variables de salida
        oferta_despues = Oferta.objects.get(pk = oferta.id)
        # Se comparan los datos. Se comprueba que la oferta no ha sufrido cambios y que se ha redirido al usuario a los
        # detalles de la oferta, puesto a que no se puede levantar el veto sobre una oferta que no está vetada.
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/oferta/detalles/{}/'.format(oferta.id))
        self.assertEqual(oferta_despues.vetada, False)
        self.assertEqual(oferta_despues.motivo_veto, None)
        # El usuario se desloguea
        self.logout()

    # Un usuario levanta el veto sobre una oferta que no existe
    def test_levanta_veto_oferta_inexistente(self):
        # Se inicializan variables y se loguea el usuario
        username = 'usuario2'
        password = 'usuario2'
        self.login(username, password)
        # Se realiza la petición para levantar el veto sobre la oferta
        response = self.client.get('/oferta/levantamiento_veto/0/')
        # Se comparan los datos. Se comprueba que al no existir la oferta, se ha redirigido al usuario al listado de
        # ofertas
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/oferta/listado/')
        # El usuario se desloguea
        self.logout()
    
    # Un usuario levanta el veto sobre una oferta en modo borrador
    def test_levanta_veto_oferta_borrador(self):
        # Se inicializan variables y se loguea el usuario
        username = 'usuario2'
        password = 'usuario2'
        oferta = Oferta.objects.filter(Q(vetada = True) & Q(borrador = True)).first()
        self.login(username, password)
        # Se realiza la petición para levantar el veto sobre la oferta
        response = self.client.get('/oferta/levantamiento_veto/{}/'.format(oferta.id))
        # Se obtienen las variables de salida
        oferta_despues = Oferta.objects.get(pk = oferta.id)
        # Se comparan los datos. Se comprueba que la oferta no ha sufrido cambios y que el usuario ha sido redirigido
        # a los detalles de la oferta puesto a que no se puede levantar el veto sobre una oferta en modo borrador.
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('oferta_detalles', kwargs = {'oferta_id': oferta.id}))
        self.assertEqual(oferta_despues.vetada, True)
        self.assertEqual(oferta.motivo_veto, oferta_despues.motivo_veto)
        # El usuario se desloguea
        self.logout()

    '''