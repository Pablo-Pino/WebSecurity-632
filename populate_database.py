from django.contrib.auth.models import User
from prueba1.models.actividad_models import Actividad
from prueba1.models.perfil_models import Usuario, Anexo
from datetime import date

# Django users

django_user_1 = User.objects.create_user(
    'usuario1', 
    'federico@gmail.com', 
    'usuario1', 
    first_name = 'Federico', 
    last_name = 'Garcia Prieto'
)

django_user_2 = User.objects.create_user(
    'usuario2', 
    'sarac@gmail.com', 
    'usuario2', 
    first_name = 'Sarah', 
    last_name = 'Connor'
)

django_user_3 = User.objects.create_user(
    'usuario3', 
    'juann@gmail.com', 
    'usuario3', 
    first_name = 'Juan', 
    last_name = 'Nieves'
)

# Usuarios

usuario_1 = Usuario(
    django_user = django_user_1,
    telefono = '123456789',
    empresa_u_equipo = 'Equipo Garcia',
    vetado = False,
    es_admin = False
)
    
usuario_2 = Usuario(
    django_user = django_user_2,
    vetado = False,
    es_admin = True
)

usuario_3 = Usuario(
    django_user = django_user_3,
    telefono = '357809201',
    empresa_u_equipo = 'Microsoft S.A.',
    vetado = False,
    es_admin = False
)

usuarios = [
    usuario_1,
    usuario_2,
    usuario_3
]

for usuario in usuarios:
    usuario.full_clean()
    usuario.save()

# Anexos

anexo_1 = Anexo(
    usuario = usuario_1,
    anexo = 'https://garcia1ertrabajo.com/'
)

anexo_2 = Anexo(
    usuario = usuario_1,
    anexo = 'https://garciaempresa.com/'
)

anexo_3 = Anexo(
    usuario = usuario_1,
    anexo = 'https://garciaofertas.com/'
)

anexo_4 = Anexo(
    usuario = usuario_1,
    anexo = 'https://garciainfo.com/'
)

anexo_5 = Anexo(
    usuario = usuario_2,
    anexo = 'https://normasdelsistema.com/'
)

anexos = [
    anexo_1,
    anexo_2,
    anexo_3,
    anexo_4,
    anexo_5
]

for anexo in anexos:
    anexo.full_clean()
    anexo.save()

# Actividades

actividad_1 = Actividad(
    titulo = 'SQL por Federico',
    enlace = 'https://sqlfederico.com/',
    descripcion = 'Un tutorial de SQLi basico por Federico. Comentarios son bienvenidos.',
    comentable = True,
    autor = usuario_1,
    borrador = False,
    vetada = False,
    fecha_creacion = date(2019, 11, 20),
    identificador = 'ACT-12345ASDxc',
)

actividad_2 = Actividad(
    titulo = 'JPQL',
    enlace = 'https://jpqlfed.com/',
    descripcion = 'Ejercicios del lenguaje JPQL, que conecta Java con bases de datos',
    comentable = False,
    autor = usuario_1,
    borrador = False,
    vetada = False,
    fecha_creacion = date(2019, 12, 12),
    identificador = 'ACT-ASDFGCVBnm',
)

actividad_3 = Actividad(
    titulo = 'Angular en detalles',
    enlace = 'https://jpqlfed.com/',
    descripcion = 'Tutoriales avanzados de Angular. Aun por completar.',
    comentable = False,
    autor = usuario_1,
    borrador = True,
    vetada = False,
    fecha_creacion = date(2020, 1, 1),
    identificador = 'ACT-forgton345',
)

actividad_4 = Actividad(
    titulo = 'Actividad de prueba',
    enlace = 'https://prueba.com/',
    descripcion = 'Para ver que todo funciona bien.',
    comentable = False,
    autor = usuario_2,
    borrador = False,
    vetada = False,
    fecha_creacion = date(2019, 11, 10),
    identificador = 'ACT-A23D5Gdefg',
)

actividad_5 = Actividad(
    titulo = 'Vendo coche',
    enlace = 'https://cochesgratis.com/',
    descripcion = 'El Ferrari esta como nuevo',
    comentable = True,
    autor = usuario_3,
    borrador = False,
    vetada = True,
    fecha_creacion = date(2019, 11, 20),
    identificador = 'ACT-456gtIOMDF',
    motivo_veto = 'Esto no es una página de compraventa'
)

actividad_6 = Actividad(
    titulo = 'Una actividad extraña',
    enlace = 'https://testing.com/',
    descripcion = 'Para ver cómo funciona la lógica de la aplicación',
    comentable = False,
    autor = usuario_1,
    borrador = True,
    vetada = True,
    fecha_creacion = date(2019, 11, 20),
    identificador = 'ACT-12345serfv',
    motivo_veto = 'El testeo es vital'
)

actividades = [
    actividad_1,
    actividad_2,
    actividad_3,
    actividad_4,
    actividad_5,
    actividad_6,
]

for actividad in actividades:
    actividad.full_clean()
    actividad.save()


