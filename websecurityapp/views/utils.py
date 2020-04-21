from websecurityapp.models.oferta_models import Solicitud, Oferta

def get_ofertas_solicitables_y_ofertas_retirables(usuario, ofertas):
    ofertas_solicitables = []
    ofertas_solicitadas = []
    ofertas_retirables = []
    solicitudes_usuario = list(Solicitud.objects.filter(usuario=usuario).only('oferta').distinct())
    for solicitud in solicitudes_usuario:
        ofertas_solicitadas.append(solicitud.oferta)
    for oferta in ofertas:
        if not oferta.cerrada and not oferta.vetada and oferta in ofertas_solicitadas:
            ofertas_retirables.append(oferta)
        elif not oferta.borrador and not oferta.cerrada and not oferta.vetada and not oferta in ofertas_solicitadas:
            es_solicitable = True
            for actividad_requerida in oferta.actividades.all():
                if not actividad_requerida in usuario.actividades_realizadas.all() or usuario == oferta.autor:
                    es_solicitable = False
                    break
                elif actividad_requerida.vetada:
                    es_solicitable = False
                    break
            if es_solicitable:
                ofertas_solicitables.append(oferta)
    return [ofertas_solicitables, ofertas_retirables]

def es_oferta_solicitable_o_retirable(usuario, oferta):
    es_solicitada = Solicitud.objects.filter(usuario=usuario, oferta=oferta).exists()
    retirable = False
    solicitable = False
    if es_solicitada:
        if not oferta.vetada and not oferta.cerrada:
            retirable = True
    else:
        if not oferta.cerrada and not oferta.vetada and not oferta.borrador:
            solicitable = True
            for actividad_requerida in oferta.actividades.all():
                if not actividad_requerida in usuario.actividades_realizadas.all() or usuario == oferta.autor:
                    solicitable = False
                    break
                elif actividad_requerida.vetada:
                    solicitable = False
                    break
    return [solicitable, retirable]