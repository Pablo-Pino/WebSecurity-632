from django import forms
from prueba1.models.actividad_models import Actividad
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator



def actividades_validas(value):
    for str_actividad_id in value:
        actividad = Actividad.objects.get(pk=int(str_actividad_id))
        if actividad.vetada or actividad.borrador:
            raise ValidationError('No se puede crear o editar una oferta con actividades vetadas o en modo borrador')

class ActividadChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return "{}   {}".format(obj.identificador, obj.titulo)

class OfertaCreacionForm(forms.Form):
    titulo = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    descripcion = forms.CharField(max_length=1000, widget=forms.Textarea(attrs={'class': 'form-control'}))
    actividades = ActividadChoiceField(queryset=Actividad.objects.filter(borrador=False, vetada=False),
            widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
            validators=[actividades_validas])

class OfertaEdicionForm(forms.Form):
    titulo = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    descripcion = forms.CharField(max_length=1000, widget=forms.Textarea(attrs={'class': 'form-control'}))
    actividades = ActividadChoiceField(queryset=Actividad.objects.filter(borrador=False, vetada=False),
            widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
            validators=[actividades_validas])
    borrador = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'form-control'}), required=False)

class OfertaVetoForm(forms.Form):
    motivo_veto = forms.CharField(max_length=1000, widget=forms.Textarea(attrs={'class': 'form-control'}))

