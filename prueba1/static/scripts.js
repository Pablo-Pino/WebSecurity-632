function alerta_redireccion(mensaje, url) {
    eval = window.confirm(mensaje)
    if (eval) 
        window.location.href = url
}