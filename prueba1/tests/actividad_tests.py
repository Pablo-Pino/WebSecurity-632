from django.test import TestCase, RequestFactory

from prueba1.models.perfil_models import Usuario
from prueba1.views.actividad_views import CreacionActividadesView

class CreacionActividadTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.get(username = 'usuario1')

    def test_crear_actividad(self):
        request = self.factory.get('/actividad/creacion')
        request.user = self.user
        response = CreacionActividadesView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        





