from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from prueba1.models.perfil_models import Usuario
from prueba1.models.actividad_models import Actividad
from prueba1.validators import past_validator

class Oferta(models.Model):
    titulo = models.CharField(max_length = 100)
    descripcion = models.CharField(max_length = 1000)
    borrador = models.BooleanField()
    cerrada = models.BooleanField()
    vetada = models.BooleanField()
    motivo_veto = models.CharField(max_length = 1000, null = True, blank = True)
    fecha_creacion = models.DateField(validators = [past_validator])
    identificador = models.CharField(max_length = 30, unique = True)
    autor = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    actividades = models.ManyToManyField(Actividad)

    def clean(self):
        super().clean()
        # No puede haber una oferta vetada sin motivo de veto
        if self.vetada and not self.motivo_veto:
            raise ValidationError('No puede haber una oferta vetada sin motivo de veto')
