from django.contrib.auth.models import User
from prueba1.models.actividad_models import Actividad, SesionActividad
from prueba1.models.perfil_models import Usuario, Anexo
from prueba1.models.oferta_models import Oferta
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
    anexo = 'http://garcia1ertrabajo.com/'
)

anexo_2 = Anexo(
    usuario = usuario_1,
    anexo = 'http://garciaempresa.com/'
)

anexo_3 = Anexo(
    usuario = usuario_1,
    anexo = 'http://garciaofertas.com/'
)

anexo_4 = Anexo(
    usuario = usuario_1,
    anexo = 'http://garciainfo.com/'
)

anexo_5 = Anexo(
    usuario = usuario_2,
    anexo = 'http://normasdelsistema.com/'
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
    enlace = 'http://sqlfederico.com/',
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
    enlace = 'http://jpqlfed.com/',
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
    enlace = 'http://jpqlfed.com/',
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
    enlace = 'http://prueba.com/',
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
    enlace = 'http://cochesgratis.com/',
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
    enlace = 'http://testing.com/',
    descripcion = 'Para ver cómo funciona la lógica de la aplicación',
    comentable = False,
    autor = usuario_1,
    borrador = True,
    vetada = True,
    fecha_creacion = date(2019, 11, 20),
    identificador = 'ACT-12345serfv',
    motivo_veto = 'El testeo es vital'
)

actividad_7 = Actividad(
    titulo = 'Mockingbird',
    enlace = 'http://localhost:8000/ejercicio/mock/1/',
    descripcion = 'Mock',
    comentable = False,
    autor = usuario_1,
    borrador = False,
    vetada = False,
    fecha_creacion = date(2019, 11, 20),
    identificador = 'ACT-332243565j',
    motivo_veto = None
)

actividad_8 = Actividad(
    titulo = 'Mockingbird2',
    enlace = 'http://localhost:8000/ejercicio/mock/2/',
    descripcion = 'Mock2',
    comentable = False,
    autor = usuario_2,
    borrador = False,
    vetada = False,
    fecha_creacion = date(2019, 11, 20),
    identificador = 'ACT-332243565g',
    motivo_veto = None
)

actividad_9 = Actividad(
    titulo = 'Mockingbird3',
    enlace = 'http://localhost:8000/ejercicio/mock/3/',
    descripcion = 'Mock3',
    comentable = False,
    autor = usuario_1,
    borrador = False,
    vetada = False,
    fecha_creacion = date(2019, 11, 20),
    identificador = 'ACT-332243565r',
    motivo_veto = None
)

actividades = [
    actividad_1,
    actividad_2,
    actividad_3,
    actividad_4,
    actividad_5,
    actividad_6,
    actividad_7,
    actividad_8,
    actividad_9,
]

for actividad in actividades:
    actividad.full_clean()
    actividad.save()

sesionactividad_1 = SesionActividad(
    usuario = usuario_2,
    actividad = actividad_7,
    token = 'ASDFGHJKL'
)

sesionactividad_2 = SesionActividad(
    usuario = usuario_1,
    actividad = actividad_8,
    token = 'TRYTYTHESGHR'
)

sesionactividad_3 = SesionActividad(
    usuario = usuario_1,
    actividad = actividad_9,
    token = '234678799876543'
)

sesionactividades = [
    sesionactividad_1,
    sesionactividad_2,
    sesionactividad_3
]

for sesionactividad in sesionactividades:
    sesionactividad.full_clean()
    sesionactividad.save()

oferta_1 = Oferta(
    titulo = 'Oferta developer',
    descripcion = 'Se busca developer',
    autor = usuario_1,
    borrador = False,
    vetada = False,
    fecha_creacion = date(2019, 11, 20),
    identificador = 'OFR-12345ASDxc',
    cerrada = False,
    motivo_veto = None,
)



oferta_2 = Oferta(
    titulo = 'JPQL',
    descripcion = 'Se busca desarrolador de querys de Spring',
    autor = usuario_1,
    borrador = False,
    vetada = False,
    fecha_creacion = date(2019, 12, 12),
    identificador = 'OFR-ASDFGCVBnm',
    cerrada = False,
    motivo_veto = None,
)

ofertas = [
   oferta_1,
   oferta_2,
]

for oferta in ofertas:
    oferta.full_clean()
    oferta.save()

oferta_1.actividades.set([actividad_1, actividad_2])
oferta_2.actividades.set([actividad_7])

for oferta in ofertas:
    oferta.full_clean()
    oferta.save()


