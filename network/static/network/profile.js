document.addEventListener('DOMContentLoaded', () => {
    // Obtener el valor de 'is_following' desde el atributo data-is-following
    const profileView = document.querySelector('#profile-view');
    const isFollowing = profileView.getAttribute('data-is-following') === 'true';
    const userId = profileView.getAttribute('data-user-id');

    // Generar el botón de follow/unfollow
    document.querySelector('#follow-div').innerHTML = `
        <button id="button-follow" class="btn-secondary btn">
            ${isFollowing ? "Unfollow" : "Follow"}
        </button>`;

    // Añadir event listener al botón de follow/unfollow
    document.querySelector('#button-follow').addEventListener('click', () => {
        const action = isFollowing ? "unfollow" : "follow";
        console.log(action);

        follow(userId, isFollowing);
    });

    function follow(profileId) {
        fetch(`/follow/${profileId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')                
            },
            body: JSON.stringify({
                isFollowing: isFollowing
            })
        })
        .then(response => response.json())
        .then(result => {
            console.log(result);
        });
    }

    // Funcion para obtener csrf token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});