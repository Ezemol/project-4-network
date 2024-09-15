document.addEventListener('DOMContentLoaded', () => {
    // Obtener el valor de 'is_following' desde el atributo data-is-following
    const profileView = document.querySelector('#profile-view');
    const isFollowing = profileView.getAttribute('data-is-following') === 'true';

    // Generar el botón de follow/unfollow
    document.querySelector('#follow-div').innerHTML = `
        <button id="button-follow" class="btn-secondary btn">
            ${isFollowing ? "Unfollow" : "Follow"}
        </button>`;

    // Añadir event listener al botón de follow/unfollow
    document.querySelector('#button-follow').addEventListener('click', () => {
        const action = isFollowing ? "unfollow" : "follow";
        console.log(action);
        // Aquí puedes hacer la petición al servidor para seguir/dejar de seguir al usuario
        // Ejemplo de lógica que puedes implementar:
        // fetch(`/follow/${profileId}`, {
        //     method: 'POST',
        //     body: JSON.stringify({ action: action })
        // });
    });
});