function alerta_eliminar(mensaje, url) {
    eval = window.confirm(mensaje)
    if (eval) 
        window.location.href = url
}