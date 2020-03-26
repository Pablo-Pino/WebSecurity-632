"""pruebaTFG URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from prueba1.views.actividad_views import ListadoActividadesView, CreacionActividadesView, EdicionActividadesView, EliminacionActividadesView, DetallesActividadesView, VetoActividadesView, LevantamientoVetoActividadesView
from prueba1.views.perfil_views import RegistroUsuarioView, DetallesPerfilView, EdicionPerfilView, CreacionAnexoView, EdicionAnexoView, EliminacionAnexoView
from prueba1.views.sesionactividad_views import SesionActividadComienzo, SesionActividadFinal
from prueba1.views.views import EjercicioMock1View, EjercicioMock2View, EjercicioMock3View
from prueba1.views.views import HomeView
from django.contrib.auth import views as auth_views
from rest_framework import routers

urlpatterns = [
    path('ejercicio/mock/1/', EjercicioMock1View.as_view(), name = 'ejercicio_mock_1'),
    path('ejercicio/mock/2/', EjercicioMock2View.as_view(), name = 'ejercicio_mock_2'),
    path('ejercicio/mock/3/', EjercicioMock3View.as_view(), name = 'ejercicio_mock_3'),
    path('sesionactividad/comienzo/<str:identificador>/', SesionActividadComienzo.as_view(), name='sesionactividad_comienzo'),
    path('sesionactividad/final/<str:identificador>/', SesionActividadFinal.as_view(), name = 'sesionactividad_final'),
    path('admin/', admin.site.urls),
    path('usuario/registro/', RegistroUsuarioView.as_view()),
    path('login/', auth_views.LoginView.as_view(template_name='perfil/login.html', redirect_authenticated_user=True), name = 'login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/')),
    path('', HomeView.as_view(), name = 'home'),
    path('actividad/listado/', ListadoActividadesView.as_view(), name = 'actividad_listado'),
    path('actividad/creacion/', CreacionActividadesView.as_view()),
    path('actividad/edicion/<int:actividad_id>/', EdicionActividadesView.as_view()),
    path('actividad/eliminacion/<int:actividad_id>/', EliminacionActividadesView.as_view()),
    path('actividad/detalles/<int:actividad_id>/', DetallesActividadesView.as_view(), name = 'actividad_detalles'),
    path('actividad/veto/<int:actividad_id>/', VetoActividadesView.as_view()),
    path('actividad/levantamiento_veto/<int:actividad_id>/', LevantamientoVetoActividadesView.as_view()),
    path('perfil/detalles/', DetallesPerfilView.as_view(), name = 'perfil_detalles'),
    path('perfil/edicion/', EdicionPerfilView.as_view(), name = 'perfil_edicion'),
    path('anexo/creacion_edicion/', CreacionAnexoView.as_view(), name = 'anexo_creacion'),
    path('anexo/creacion_edicion/<int:anexo_id>/', EdicionAnexoView.as_view(), name = 'anexo_edicion'),
    path('anexo/eliminacion/<int:anexo_id>/', EliminacionAnexoView.as_view(), name = 'anexo_eliminacion'),
]
