function alerta_redireccion(mensaje, url) {
    eval = window.confirm(mensaje);
    if (eval) 
        window.location.href = url;
}

function selecciona_pagina(n_pagina, pagina_param) {
    if (n_pagina != null) {
        uri = encodeURI('?' + pagina_param + '=' + n_pagina);
        window.location.href = uri;
    } else {
        window.location.href = '';
    }
}

async function inicia_sesionactividad(identificador) {
    fetch(
        'https://localhost:8000/sesionactividad/comienzo/' + identificador + '/'
    ).then(
        (response) => {
            divAlert = document.getElementById('alert-div');
            divAlert.innerHTML = '';
            divMensaje = document.createElement('div');
            divMensaje.id = 'message-div';
            if (response.status == 200)
                divMensaje.className = 'alert alert-success';
            else if (response.status == 500)
                divMensaje.className = 'alert alert-danger';
            divAlert.appendChild(divMensaje);
            return response.json();
    }).then(
        (data) => {
            console.log(data);
            Cookies.set('sesionactividad_token', data['token']);
            // console.log(Cookies.get('sesionactividad_token'));
            // console.log(Cookies.get('csrftoken'));
            divMensaje = document.getElementById('message-div');
            messageText = document.createTextNode(data['status']);
            divMensaje.appendChild(messageText);
    });
}

async function finaliza_sesionactividad(identificador) {
    token = Cookies.get('sesionactividad_token');
    csrfToken = Cookies.get('csrftoken');
    fetch('https://localhost:8000/sesionactividad/final/' + identificador + '/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({token: token})
    }).then(
        (response) => {
            jsonResponse = response.json();
            divAlert = document.getElementById('alert-div');
            divAlert.innerHTML = '';
            divMensaje = document.createElement('div');
            divMensaje.id = 'message-div';
            if (response.status == 201)
                divMensaje.className = 'alert alert-success';
            else if (response.status == 500)
                divMensaje.className = 'alert alert-danger';
            divAlert.appendChild(divMensaje);
            return jsonResponse;
        }
    )
    .then(
        (data) => {
            // console.log(data);
            divMensaje = document.getElementById('message-div');
            messageText = document.createTextNode(data.status);
            divMensaje.appendChild(messageText);
        }
    );
}