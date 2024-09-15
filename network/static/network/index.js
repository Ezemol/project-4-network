document.addEventListener('DOMContentLoaded', () => {

    // Accede al contenido del enlace con el id 'profile'
    var username = document.getElementById('profile').textContent.trim();
    document.querySelector("#profile").addEventListener('click', () => load_profile(username));
    
})

function load_profile(username) {
    fetch(`/profile/${username}/`)
        .then(response => response.json())
        .then(posts => {
            // Print posts
            console.log(posts);

            // Ordenar por orden cronológico
            posts.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

            posts.forEach(post => {
                const newDiv = document.createElement('div');

                newDiv.id =` post-item-${post.id}`;

                // Agregar cada post
                newDiv.innerHTML = `
                            <h1>${username}</h1>
                            <div>
                                {% if posts %}
                                    <p>Followers: {{ num_followers }}</p>
                                    <p>Following {{ num_following }} </p>
                                    <hr>
                                    ${post.timestamp}
                                    <hr>
                                    <p>Post made by:${username}</p>
                                    <p>${post.body}</p>
                                {% else %}
                                    <h3>No active posts</h3>
                                {% endif %}
                `;

                document.querySelector('#profile-view').appendChild(newDiv);
            })

        })
        .catch(error => {
            // Manejo de errores
            console.error('Invalid posts', error)
        })
}   