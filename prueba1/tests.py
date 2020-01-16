from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist

from selenium.webdriver.firefox.webdriver import WebDriver
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

from prueba1.models.perfil_models import Usuario
from prueba1.models.actividad_models import Actividad
from prueba1.views.actividad_views import CreacionActividadesView

import datetime

class CreacionActividadTestCase(StaticLiveServerTestCase):
    fixtures = ['dumpdata.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def login(self, username, password):
        self.selenium.get('%s%s' % (self.live_server_url, '/login'))
        input_username = self.selenium.find_element_by_id('id_username')
        input_password = self.selenium.find_element_by_id('id_password')
        input_username.send_keys(username)
        input_password.send_keys(password)
        input_submit = self.selenium.find_element_by_xpath('//input[@type="submit"]')
        input_submit.click()
        user = User.objects.get(username=username)
        h2_home = self.selenium.find_element_by_tag_name('h2')
        self.assertEqual(self.selenium.current_url, self.live_server_url + '/')
        self.assertEqual('Bienvenido {} {}'.format(user.first_name, user.last_name) in h2_home.text, True)
        usuario = Usuario.objects.get(django_user = user)
        return usuario

    def logout(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/logout'))
    
    def test_crear_actividad(self):
        self.login('usuario1', 'usuario1')
        self.selenium.get('%s%s' % (self.live_server_url, '/actividad/creacion'))
        title_text = self.selenium.find_element_by_tag_name('h1').text
        self.assertEqual('Creacion de actividades' in title_text, True)
        input_descripcion = self.selenium.find_element_by_id('id_descripcion')
        input_titulo = self.selenium.find_element_by_id('id_titulo')
        input_comentable = self.selenium.find_element_by_id('id_comentable')
        input_enlace = self.selenium.find_element_by_id('id_enlace')
        input_descripcion.send_keys('descripcion')
        input_titulo.send_keys('titulo')
        input_enlace.send_keys('https://enlace.com')
        input_comentable.click()
        input_submit = self.selenium.find_element_by_xpath('//input[@type="submit"]')
        input_submit.click() 
        message_success = self.selenium.find_element_by_class_name('alert-success')
        output_descripcion = self.selenium.find_element_by_xpath('//p[text()="Descripcion : {}"]'.format('descripcion'))
        output_titulo = self.selenium.find_element_by_xpath('//p[text()="Titulo : {}"]'.format('titulo'))
        output_enlace = self.selenium.find_element_by_xpath('//a[@href="{}"]'.format('https://enlace.com'))
        nueva_actividad = Actividad.objects.order_by('-id').first()
        self.assertEqual('{}/actividad/detalles/{}/'.format(self.live_server_url, nueva_actividad.id), self.selenium.current_url)
        self.assertEqual(message_success.text, 'Se ha creado la actividad con exito')
        self.assertEqual(output_descripcion != None, True)
        self.assertEqual(output_titulo != None, True)
        self.assertEqual(output_enlace != None, True)
        self.logout()

    def test_crear_actividad_con_errores(self):
        self.login('usuario1', 'usuario1')
        self.selenium.get('%s%s' % (self.live_server_url, '/actividad/creacion'))
        title_text = self.selenium.find_element_by_tag_name('h1').text
        self.assertEqual('Creacion de actividades' in title_text, True)
        input_descripcion = self.selenium.find_element_by_id('id_descripcion')
        input_titulo = self.selenium.find_element_by_id('id_titulo')
        input_comentable = self.selenium.find_element_by_id('id_comentable')
        input_enlace = self.selenium.find_element_by_id('id_enlace')
        input_descripcion.send_keys('')
        input_titulo.send_keys('')
        input_enlace.send_keys('a')
        input_submit = self.selenium.find_element_by_xpath('//input[@type="submit"]')
        input_submit.click() 
        error_titulo = self.selenium.find_element_by_xpath('//input[@id="id_titulo"]/following::div[@class="invalid-feedback"][1]')
        error_descripcion = self.selenium.find_element_by_xpath('//input[@id="id_descripcion"]/following::div[@class="invalid-feedback"][1]')
        error_enlace = self.selenium.find_element_by_xpath('//input[@id="id_enlace"]/following::div[@class="invalid-feedback"][1]')
        self.assertEqual(error_titulo.text, 'Este campo es obligatorio.')
        self.assertEqual(error_descripcion.text, 'Este campo es obligatorio.')
        self.assertEqual(error_enlace.text, 'Introduzca una URL válida.')
        self.logout()

    def test_crear_actividad_sin_autenticar(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/actividad/creacion'))
        message_danger = self.selenium.find_element_by_class_name('alert-danger')
        self.assertEqual(self.selenium.current_url, self.live_server_url + '/')
        self.assertEqual(message_danger.text, 'Se requiere estar autenticado')
    
    def test_listado_actividades(self):
        # Se accede al listado de actividades como el usuario1
        self.login('usuario1', 'usuario1')
        # Se accede al listado de actividades
        self.selenium.get('%s%s' % (self.live_server_url, '/actividad/listado'))
        # Se comprueba que aparecen las actividades correctas
        usuario = Usuario.objects.get(django_user__username = 'usuario1')
        actividades_esperadas = Actividad.objects.filter(Q(autor=usuario) | Q(borrador=False, vetada=False)).distinct().order_by('id')
        actividades_mostradas = self.selenium.find_elements_by_tag_name('tr')
        self.assertEqual(len(actividades_esperadas), len(actividades_mostradas) - 1)
        # Se comprueba que solo aparecen los botones necesarios
        self.evaluar_columnas_listado_actividades(actividades_esperadas, usuario)
        # Se cierra sesion
        self.logout()
        # Se accede al listado de actividades como el usuario2
        self.login('usuario2', 'usuario2')
        # Se accede al listado de actividades
        self.selenium.get('%s%s' % (self.live_server_url, '/actividad/listado'))
        # Se comprueba que aparecen las actividades correctas
        usuario = Usuario.objects.get(django_user__username = 'usuario2')
        actividades_esperadas = Actividad.objects.filter(Q(autor=usuario) | Q(borrador=False)).distinct().order_by('id')
        actividades_mostradas = self.selenium.find_elements_by_tag_name('tr')
        self.assertEqual(len(actividades_esperadas), len(actividades_mostradas) - 1)
        # Se comprueba que solo aparecen los botones necesarios
        self.evaluar_columnas_listado_actividades(actividades_esperadas, usuario)
        # Se cierra sesion
        self.logout()
        # Se accede al listado de actividades como el usuario3
        self.login('usuario3', 'usuario3')
        # Se accede al listado de actividades
        self.selenium.get('%s%s' % (self.live_server_url, '/actividad/listado'))
        # Se comprueba que aparecen las actividades correctas
        usuario = Usuario.objects.get(django_user__username = 'usuario3')
        actividades_esperadas = Actividad.objects.filter(Q(autor=usuario) | Q(borrador=False, vetada=False)).distinct().order_by('id')
        actividades_mostradas = self.selenium.find_elements_by_tag_name('tr')
        self.assertEqual(len(actividades_esperadas), len(actividades_mostradas) - 1)
        # Se comprueba que solo aparecen los botones necesarios
        self.evaluar_columnas_listado_actividades(actividades_esperadas, usuario)
        # Se cierra sesion
        self.logout()

    def test_editar_actividad(self):
        self.login('usuario1', 'usuario1')
        usuario = Usuario.objects.get(django_user__username = 'usuario1')
        actividad = Actividad.objects.get(autor = usuario, borrador = True)
        self.selenium.get('%s%s' % (self.live_server_url, '/actividad/edicion/{}/'.format(actividad.id)))
        title_text = self.selenium.find_element_by_tag_name('h1').text
        self.assertEqual('Edicion de actividades' in title_text, True)
        input_descripcion = self.selenium.find_element_by_id('id_descripcion')
        input_titulo = self.selenium.find_element_by_id('id_titulo')
        input_comentable = self.selenium.find_element_by_id('id_comentable')
        input_enlace = self.selenium.find_element_by_id('id_enlace')
        input_borrador = self.selenium.find_element_by_id('id_borrador')
        input_descripcion.clear()
        input_descripcion.send_keys('descripcioneditada')
        input_titulo.clear()
        input_titulo.send_keys('tituloeditado')
        input_enlace.clear()
        input_enlace.send_keys('https://enlaceeditado.com')
        input_comentable.click()
        input_submit = self.selenium.find_element_by_xpath('//input[@type="submit"]')
        input_submit.click() 
        message_success = self.selenium.find_element_by_class_name('alert-success')
        output_descripcion = self.selenium.find_element_by_xpath('//p[text()="Descripcion : {}"]'.format('descripcioneditada'))
        output_titulo = self.selenium.find_element_by_xpath('//p[text()="Titulo : {}"]'.format('tituloeditado'))
        output_enlace = self.selenium.find_element_by_xpath('//a[@href="{}"]'.format('https://enlaceeditado.com'))
        self.assertEqual('{}/actividad/detalles/{}/'.format(self.live_server_url, actividad.id), self.selenium.current_url)
        self.assertEqual(message_success.text, 'Se ha editado la actividad con exito')
        self.assertEqual(output_descripcion != None, True)
        self.assertEqual(output_titulo != None, True)
        self.assertEqual(output_enlace != None, True)
        self.logout()

    def test_editar_actividad_vacia(self):
        self.login('usuario1', 'usuario1')
        usuario = Usuario.objects.get(django_user__username = 'usuario1')
        actividad = Actividad.objects.get(autor = usuario, borrador = True)
        self.selenium.get('%s%s' % (self.live_server_url, '/actividad/edicion/{}/'.format(actividad.id)))
        title_text = self.selenium.find_element_by_tag_name('h1').text
        self.assertEqual('Edicion de actividades' in title_text, True)
        input_descripcion = self.selenium.find_element_by_id('id_descripcion')
        input_titulo = self.selenium.find_element_by_id('id_titulo')
        input_comentable = self.selenium.find_element_by_id('id_comentable')
        input_enlace = self.selenium.find_element_by_id('id_enlace')
        input_descripcion.clear()
        input_titulo.clear()
        input_enlace.clear()
        input_submit = self.selenium.find_element_by_xpath('//input[@type="submit"]')
        input_submit.click() 
        error_titulo = self.selenium.find_element_by_xpath('//input[@id="id_titulo"]/following::div[@class="invalid-feedback"][1]')
        error_descripcion = self.selenium.find_element_by_xpath('//input[@id="id_descripcion"]/following::div[@class="invalid-feedback"][1]')
        error_enlace = self.selenium.find_element_by_xpath('//input[@id="id_enlace"]/following::div[@class="invalid-feedback"][1]')
        self.assertEqual(error_titulo.text, 'Este campo es obligatorio.')
        self.assertEqual(error_descripcion.text, 'Este campo es obligatorio.')
        self.assertEqual(error_enlace.text, 'Este campo es obligatorio.')
        self.logout()

    def test_editar_actividad_sin_autenticar(self):
        actividad = Actividad.objects.filter(borrador=True).first()
        self.selenium.get('%s%s' % (self.live_server_url, '/actividad/edicion/{}/'.format(actividad.id)))
        message_danger = self.selenium.find_element_by_class_name('alert-danger')
        self.assertEqual(self.selenium.current_url, self.live_server_url + '/actividad/listado/')
        self.assertEqual(message_danger.text, 'Se requiere estar autenticado')

    def test_editar_usuario_incorrecto(self):
        usuario = self.login('usuario2', 'usuario2')
        actividad = Actividad.objects.exclude(autor=usuario).filter(borrador=True).first()
        self.selenium.get('%s%s' % (self.live_server_url, '/actividad/edicion/{}/'.format(actividad.id)))
        message_danger = self.selenium.find_element_by_class_name('alert-danger')
        self.assertEqual(self.selenium.current_url, self.live_server_url + '/actividad/listado/')
        self.assertEqual(message_danger.text, 'No se poseen permisos para editar la actividad')
        self.logout()
    
    def editar_actividad_no_borrador(self):
        usuario = self.login('usuario1', 'usuario1')
        actividad = Actividad.objects.filter(autor=usuario, borrador=False).first()
        self.selenium.get('%s%s' % (self.live_server_url, '/actividad/edicion/{}/'.format(actividad.id)))
        message_danger = self.selenium.find_element_by_class_name('alert-danger')
        self.assertEqual(self.selenium.current_url, self.live_server_url + '/actividad/listado/')
        self.assertEqual(message_danger.text, 'No se poseen permisos para editar la actividad')
        self.logout()
    
    def test_eliminar_actividad(self):
        self.login('usuario1', 'usuario1')
        usuario = Usuario.objects.get(django_user__username = 'usuario1')
        actividad = Actividad.objects.get(autor = usuario, borrador = True)
        self.selenium.get('%s%s' % (self.live_server_url, '/actividad/listado/'.format(actividad.id)))
        numero_actividades_antes = Actividad.objects.count()
        actividades_listado_antes = self.selenium.find_elements_by_xpath('//tbody/child::tr')
        self.selenium.get('%s%s' % (self.live_server_url, '/actividad/eliminacion/{}/'.format(actividad.id)))
        self.assertEqual(self.selenium.current_url, self.live_server_url + '/actividad/listado/')
        # Aparece el mensaje de eliminacion correcta
        message_success = self.selenium.find_element_by_class_name('alert-success')
        self.assertEqual(message_success.text, 'Se ha eliminado la actividad con exito')
        # Se ha eliminado la actividad de la base de datos
        numero_actividades_despues = Actividad.objects.count()
        self.assertEqual(numero_actividades_antes, numero_actividades_despues + 1)  
        actividad_eliminada = True
        try:
            Actividad.objects.get(pk = actividad.id)
            actividad_eliminada = False
        except ObjectDoesNotExist as e:
            pass
        self.assertEqual(actividad_eliminada, True)
        actividades_listado_despues = self.selenium.find_elements_by_xpath('//tbody/child::tr')
        self.assertEqual(len(actividades_listado_antes), len(actividades_listado_despues) + 1)
        self.logout()      

    def test_eliminar_actividad_sin_autenticar(self):
        actividad = Actividad.objects.filter(borrador=True).first()
        self.selenium.get('%s%s' % (self.live_server_url, '/actividad/eliminacion/{}/'.format(actividad.id)))
        message_danger = self.selenium.find_element_by_class_name('alert-danger')
        self.assertEqual(self.selenium.current_url, self.live_server_url + '/actividad/listado/')
        self.assertEqual(message_danger.text, 'No tienes los permisos o requisitos necesarios para realizar esta accion')

    def test_eliminar_usuario_incorrecto(self):
        usuario = self.login('usuario2', 'usuario2')
        actividad = Actividad.objects.filter(borrador=True).exclude(autor=usuario).first()
        self.selenium.get('%s%s' % (self.live_server_url, '/actividad/eliminacion/{}/'.format(actividad.id)))
        message_danger = self.selenium.find_element_by_class_name('alert-danger')
        self.assertEqual(self.selenium.current_url, self.live_server_url + '/actividad/listado/')
        self.assertEqual(message_danger.text, 'No tienes los permisos o requisitos necesarios para realizar esta accion')

    def test_eliminar_actividad_no_borrador(self):
        usuario = self.login('usuario1', 'usuario1')
        actividad = Actividad.objects.filter(borrador=False, autor=usuario).first()
        self.selenium.get('%s%s' % (self.live_server_url, '/actividad/eliminacion/{}/'.format(actividad.id)))
        message_danger = self.selenium.find_element_by_class_name('alert-danger')
        self.assertEqual(self.selenium.current_url, self.live_server_url + '/actividad/listado/')
        self.assertEqual(message_danger.text, 'No se poseen los permisos o requisitos necesarios para realizar esta accion')
        
    def evaluar_columnas_listado_actividades(self, actividades_esperadas, usuario):
        i = 2
        for a in actividades_esperadas:
            titulo = self.selenium.find_element_by_xpath('//tbody/child::tr[{}]/child::td[1]'.format(i)).text
            self.assertEqual(titulo, a.titulo)
            descripcion = self.selenium.find_element_by_xpath('//tbody/child::tr[{}]/child::td[2]'.format(i)).text
            self.assertEqual(descripcion, a.descripcion)
            fecha_creacion = self.selenium.find_element_by_xpath('//tbody/child::tr[{}]/child::td[3]'.format(i)).text
            self.assertEqual(fecha_creacion, a.fecha_creacion.strftime('%d/%m/%Y'))
            autor = self.selenium.find_element_by_xpath('//tbody/child::tr[{}]/child::td[4]'.format(i)).text
            self.assertEqual(autor, '{} {}'.format(a.autor.django_user.first_name, a.autor.django_user.last_name))
            boton_detalles = self.selenium.find_element_by_xpath('//tbody/child::tr[{}]/child::td[5]/child::button'.format(i))
            self.assertEqual(boton_detalles.get_attribute('onclick'), 'window.location.href = \'/actividad/detalles/{}/\''.format(a.id))
            j = 6
            try:
                boton_editar = self.selenium.find_element_by_xpath('//tbody/child::tr[{}]/child::td[{}]/child::button'.format(i, j))
                if usuario == a.autor and a.borrador:
                    self.assertEqual(boton_editar.get_attribute('onclick'), 'window.location.href = \'/actividad/edicion/{}/\''.format(a.id))
                    boton_editar = True
                    j = j + 1
                else:
                    self.assertEqual(boton_editar.get_attribute('onclick') == 'window.location.href = \'/actividad/edicion/{}/\''.format(a.id), False)
                    boton_editar = False
            except NoSuchElementException:
                boton_editar = False
            self.assertEqual(usuario == a.autor and a.borrador, boton_editar)
            try:
                boton_eliminar = self.selenium.find_element_by_xpath('//tbody/child::tr[{}]/child::td[{}]/child::button'.format(i, j))
                if usuario == a.autor and a.borrador:
                    self.assertEqual(boton_eliminar.get_attribute('onclick'), 'alerta_eliminar(\'Desea eliminar esta actividad ?\', \'/actividad/eliminacion/{}/\')'.format(a.id))
                    boton_eliminar = True
                    j = j + 1
                else:
                    self.assertEqual(boton_eliminar.get_attribute('onclick') == 'alerta_eliminar(\'Desea eliminar esta actividad ?\', \'/actividad/eliminacion/{}/\')'.format(a.id), False)
                    boton_eliminar = False
            except NoSuchElementException:
                boton_eliminar = False
            self.assertEqual(usuario == a.autor and a.borrador, boton_eliminar)
            try:
                boton_veto = self.selenium.find_element_by_xpath('//tbody/child::tr[{}]/child::td[{}]/child::button'.format(i, j))
                if usuario.es_admin and not a.borrador and not a.vetada:
                    self.assertEqual(boton_veto.get_attribute('onclick'), 'window.location.href = \'/actividad/veto/{}/\''.format(a.id))
                    boton_veto = True
                    j = j + 1
                else:
                    self.assertEqual(boton_veto.get_attribute('onclick') == 'window.location.href = \'/actividad/veto/{}/\''.format(a.id), False)
                    boton_veto = False
            except NoSuchElementException:
                boton_veto = False
            self.assertEqual(usuario.es_admin and not a.borrador and not a.vetada, boton_veto)
            i = i + 1

    '''
    def test_vetar_actividad(self):

    def test_vetar_actividad_vacia(self):

    def test_vetar_actividad_no_administrador(self):

    def test_vetar_actividad_borrador(self):

    def test_vetar_actividad_vetada(self):

    def test_levantar_veto_actividad(self):

    def test_levantar_veto_actividad_no_administrador(self):

    def test_levantar_veto_actividad_no_vetada(self):
    '''