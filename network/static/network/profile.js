document.addEventListener('DOMContentLoaded', () => {
    // Obtener el valor de 'is_following' desde el atributo data-is-following
    const profileView = document.querySelector('#profile-view');

    if (profileView) {
        let isFollowing = profileView.getAttribute('data-is-following') === 'true';  // Convierte el valor a booleano
        const profileId = profileView.getAttribute('data-user-id');  // Obtiene el ID del perfil

        // Declaro variable del div del follow
        const followDiv = document.querySelector('#follow-div');

        if (followDiv) {
            // Agrego boton de follow/unfollow
            followDiv.innerHTML = `
            <button id="button-follow" class="btn-secondary btn">
                ${isFollowing ? "Unfollow" : "Follow"}  
            </button>`; // Cambia el texto del botón según el estado

            // Añadir event listener al botón de follow/unfollow
            document.querySelector('#button-follow').addEventListener('click', () => {
                const action = isFollowing ? "unfollow" : "follow";  // Define la acción a realizar
                console.log(action);  // Muestra la acción en la consola

                follow(profileId, isFollowing);  // Llama a la función follow
            });
        }
    }

    // Selecciona todos los botones de edición
    document.querySelectorAll(`[id^="edit-post-button"]`).forEach(button => {
        // Añade un event listener a cada boton
        button.addEventListener('click', () => {
            const postId = button.id.split('-').pop(); // Obtiene el postId del boton
            editPost(postId); // Llama a la función editPost pasando el id del boton seleccionado.
        });
    });

    // Selecciona todos los botones de like
    const likeButton = document.querySelectorAll(`[id^="like-post-button"]`).forEach(button => {
        button.addEventListener('click', () => {
            const postId = button.id.split('-').pop(); // Obtiene el postId del boton
            const isLiked = document.querySelector(`#like-post-button-${postId}`).textContent.trim();
            // Pasa el id del post y si ya likeó o no este post.
            if (isLiked === 'Like') {
                likePost(postId, true); // Llama a la función likePost pasando el id del boton seleccionado.
            } else {
                likePost(postId, false);
            }
        });
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
    
    // Funcion para editar texto del post
    function editPost(postId) {
        const postBody = document.querySelector(`#post-body[data-post-id="${postId}"]`);
        const originalText = postBody.textContent;

        postBody.innerHTML = `
            <textarea id="textarea-${postId}">${originalText}</textarea>
            <button id="save-post-${postId}" class="btn btn-primary">Save</button>
        `

        document.querySelector(`#save-post-${postId}`).addEventListener('click', () => {
            const updatedContent = document.querySelector(`#textarea-${postId}`).value;
            savePost(postId, updatedContent);
        })
    }

    // Save post function
    function savePost(postId, updatedContent) {
        fetch(`/edit_post/${postId}/`, {
            method: 'POST', 
            headers: {
                'Content-type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                content: updatedContent
            })
        })
        .then(response => response.json())
        .then(result => {
            // Mostrar en pantalla
            console.log(result);

            if (result.success) {
                // Actualiza el contenido del post en la página
                const postBody = document.querySelector(`#post-body[data-post-id="${postId}"]`);
                postBody.innerHTML = result.updatedContent;


            } else {
                console.error('Error changing the post.', result.error);
            }
        })
        .catch(error => {
            console.error('Error: ', error);
        })
    }

    // Función para like/dislike post
    function likePost(postId, isLiked) {
        fetch(`/like_post/${postId}/`, {
            method: 'POST',
            headers: {
                'Content-type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                isLiked: isLiked
            })
        }) 
        .then(response => response.json())
        .then(result => {
            console.log(result);

            if (result.success) {
                const likeButton = document.querySelector(`#like-post-button-${postId}`);
                likeButton.innerHTML =  `${isLiked ? "Unlike" : "Like"}`;
            } else {
                console.error('Error liking the post.', result.error);
            }

        })
        .catch(error => {
            console.error('Error: ', error);
        })
    }
});