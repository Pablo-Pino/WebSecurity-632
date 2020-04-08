from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
from rest_framework.parsers import JSONParser
from prueba1.serializers.sesionactividad_serializer import SesionActividadSerializer
from prueba1.models.actividad_models import SesionActividad, Actividad
from prueba1.models.perfil_models import Usuario
from prueba1.services import sesionactividad_services
from django.views.decorators.csrf import csrf_exempt

class SesionActividadComienzo(APIView):

    def get(self, request, identificador, format=None):
        # Crea la sesion
        actividad = Actividad.objects.get(identificador = identificador)
        try:
            sesionactividad = sesionactividad_services.crea_sesionactividad(request, actividad)
        except Usuario.DoesNotExist as e:
            json_response = JsonResponse({'status': 'Se debe iniciar sesión para acceder a la actividad'}, status=500, safe=False)
            return json_response
        # Manda el token
        serializer = SesionActividadSerializer(sesionactividad)
        data = serializer.data
        data['status'] = 'Se ha comenzado la actividad correctamente'
        json_response = JsonResponse(data, safe=False)
        return json_response

class SesionActividadFinal(APIView):
    parser_classes = [JSONParser]

    def post(self, request, identificador, format=None):
        if request.user.id == None:
            json_response = JsonResponse({'status': 'El usuario debe estar autenticado'}, status=500)
            return json_response
        try:
            serializer = SesionActividadSerializer(data=request.data)
            if serializer.is_valid():
                # Elimina la sesion
                actividad = Actividad.objects.get(identificador = identificador)
                sesionactividad_services.elimina_sesionactividad(request, actividad)
                # Manda una respuesta
                sesionactividad_services.añade_actividad_realizada(request, actividad)
                json_response = JsonResponse({'status': 'Se ha realizado correctamente la actividad'}, status=201)
                return json_response
            json_response = JsonResponse(serializer.errors, status=500)
        except Exception as e:
            json_response = JsonResponse({'status': 'Se ha producido un error en la conexión con el servidor'}, status=500)
        return json_response


