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

# Un usuario elimina una actividad
def test_eliminar_actividad(self):
    self.login('usuario1', 'usuario1')
    usuario = Usuario.objects.get(django_user__username = 'usuario1')
    actividad = Actividad.objects.filter(Q(autor = usuario) & Q(borrador = True)).first()
    self.selenium.get('%s%s' % (self.live_server_url, '/actividad/listado/'.format(actividad.id)))
    numero_actividades_antes = Actividad.objects.count()
    actividades_listado_antes = self.selenium.find_elements_by_xpath('//tbody/child::tr')
    boton_eliminar = self.selenium.find_element_by_xpath('//button[@id="button_eliminar"]')
    boton_eliminar.click()    
    self.selenium.switch_to.alert.accept()
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