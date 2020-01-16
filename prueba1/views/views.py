from django.shortcuts import render
from django.http import HttpResponse, QueryDict, HttpResponseRedirect
from django.views import View
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.urls import reverse

from prueba1.exceptions import UnallowedUserException
from prueba1.models.perfil_models import Usuario

# Create your views here.

class HomeView(View):
    template_name = 'master_page/master_page.html'
    
    def get(self, request):
        context = {}
        user = request.user
        if user:
            context.update({'user': user})
        return render(request, self.template_name, context)
    
    


