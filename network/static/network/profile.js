document.addEventListener('DOMContentLoaded', () => {
    // Obtener el valor de 'is_following' desde el atributo data-is-following
    const profileView = document.querySelector('#profile-view');
    let isFollowing = profileView.getAttribute('data-is-following') === 'true';  // Convierte el valor a booleano
    const profileId = profileView.getAttribute('data-user-id');  // Obtiene el ID del perfil
    
    // Generar el botón de follow/unfollow
    document.querySelector('#follow-div').innerHTML = `
        <button id="button-follow" class="btn-secondary btn">
            ${isFollowing ? "Unfollow" : "Follow"}  
        </button>`; // Cambia el texto del botón según el estado

    // Añadir event listener al botón de follow/unfollow
    document.querySelector('#button-follow').addEventListener('click', () => {
        const action = isFollowing ? "unfollow" : "follow";  // Define la acción a realizar
        console.log(action);  // Muestra la acción en la consola

        follow(profileId, isFollowing);  // Llama a la función follow
    });

    function follow(profileId, isFollowing) {
        // Realiza una solicitud para seguir/desseguir al usuario
        fetch(`/follow/${profileId}/`, {
            method: 'POST',  // Método de la solicitud
            headers: {
                'Content-Type': 'application/json',  // Tipo de contenido
                'X-CSRFToken': getCookie('csrftoken')  // Incluye el token CSRF
            },
            body: JSON.stringify({
                isFollowing: isFollowing  // Envía el estado actual de seguimiento
            })
        })
        .then(response => response.json())  // Convierte la respuesta a JSON
        .then(result => {
            console.log(result);  // Muestra el resultado en la consola
            
            // Actualiza el botón basado en la respuesta
            if (result.is_following !== undefined) {  // Verifica si el campo is_following está en la respuesta
                isFollowing = result.is_following;  // Actualiza la variable isFollowing
                document.querySelector('#button-follow').innerText = isFollowing ? "Unfollow" : "Follow";  // Cambia el texto del botón
            }
        })
        .catch(error => {
            console.error('Error:', error);  // Muestra el error en la consola
            alert('An error occurred while trying to follow/unfollow the user.');  // Muestra un mensaje de error al usuario
        });
    }

    // Funcion para obtener csrf token
    function getCookie(name) {
        let cookieValue = null;  // Inicializa el valor del cookie
        if (document.cookie && document.cookie !== '') {  // Verifica si hay cookies
            const cookies = document.cookie.split(';');  // Separa las cookies en un array
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();  // Limpia los espacios en blanco
                if (cookie.substring(0, name.length + 1) === (name + '=')) {  // Busca la cookie por su nombre
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));  // Decodifica el valor de la cookie
                    break;  // Sale del bucle una vez encontrada
                }
            }
        }
        return cookieValue;  // Devuelve el valor de la cookie
    }
});