from django.test import TestCase, LiveServerTestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Post, Profile, User  # Asegúrate de que el modelo Post esté importado
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time


"""
No estan del todo bien los tests, los voy a dejar aqui solamente por si los quiero corregir en un futuro.
El proyecto ya está terminado, y manualmente todos los tests son correctos.
"""

class AuthTests(TestCase):

    def setUp(self):
        # Configura un usuario para usar en las pruebas
        self.username = 'testuser'
        self.password = 'testpassword123'
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def test_register_user(self):
        # Probar el registro de un nuevo usuario
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword123',
            'confirmation': 'newpassword123',
        })
        self.assertEqual(response.status_code, 302)  # Redirige después de un registro exitoso
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_user_existing_username(self):
        # Probar el registro con un nombre de usuario existente
        response = self.client.post(reverse('register'), {
            'username': self.username,
            'email': 'testuser@example.com',
            'password': 'newpassword123',
            'confirmation': 'newpassword123',
        })
        self.assertEqual(response.status_code, 200)  # Debería quedarse en la misma página
        self.assertContains(response, "A user with that username already exists.")

    def test_login_user(self):
        # Probar el inicio de sesión con credenciales válidas
        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': self.password,
        })
        self.assertEqual(response.status_code, 302)  # Redirige después de un inicio de sesión exitoso
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_invalid_user(self):
        # Probar el inicio de sesión con credenciales inválidas
        response = self.client.post(reverse('login'), {
            'username': 'invaliduser',
            'password': 'invalidpassword',
        })
        self.assertEqual(response.status_code, 200)  # Debería quedarse en la misma página
        self.assertContains(response, "Please enter a correct username and password.")

    def test_logout_user(self):
        # Probar el cierre de sesión
        self.client.login(username=self.username, password=self.password)  # Iniciar sesión primero
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Redirige después de un cierre de sesión exitoso
        self.assertFalse(response.wsgi_request.user.is_authenticated)

class NavigationTests(TestCase):

    def setUp(self):
        # Configura un usuario para usar en las pruebas
        self.username = 'testuser'
        self.password = 'testpassword123'
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def test_navigation_links(self):
        # Probar la navegación de la barra de navegación
        # Caso de usuario autenticado
        self.client.login(username=self.username, password=self.password)

        response = self.client.get(reverse('index'))  # Página de inicio
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('profile', args=[self.username]))  # Página de perfil
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('new_post'))  # Página de nuevas publicaciones
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('following_posts'))  # Página de publicaciones de usuarios seguidos
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('logout'))  # Página de cierre de sesión
        self.assertEqual(response.status_code, 302)  # Redirige después de cerrar sesión

    def test_navigation_links_not_authenticated(self):
        # Probar la navegación de la barra de navegación para un usuario no autenticado
        response = self.client.get(reverse('index'))  # Página de inicio
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('login'))  # Página de inicio de sesión
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('register'))  # Página de registro
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('following_posts'))  # Intento de acceso a la página de publicaciones de usuarios seguidos
        self.assertEqual(response.status_code, 302)  # Redirige a la página de inicio de sesión

class PostTests(TestCase):

    def setUp(self):
        # Configura un usuario y una publicación para usar en las pruebas
        self.username = 'testuser'
        self.password = 'testpassword123'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.client.login(username=self.username, password=self.password)  # Inicia sesión

    def test_create_post(self):
        # Probar la creación de una nueva publicación
        response = self.client.post(reverse('new_post'), {
            'post_made': 'This is a test post.'
        })
        self.assertEqual(response.status_code, 302)  # Redirige después de crear una publicación
        self.assertTrue(Post.objects.filter(body='This is a test post.').exists())

    def test_edit_post(self):
        # Probar la edición de una publicación existente
        post = Post.objects.create(user=self.user, body='Initial body')
        response = self.client.post(reverse('edit_post', args=[post.id]), {
            'post_made': 'Updated body'
        })
        self.assertEqual(response.status_code, 302)  # Redirige después de editar
        post.refresh_from_db()  # Actualiza la instancia del modelo
        self.assertEqual(post.body, 'Updated body')

class LikeTests(TestCase):

    def setUp(self):
        # Configura un usuario y una publicación para usar en las pruebas
        self.username = 'testuser'
        self.password = 'testpassword123'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.client.login(username=self.username, password=self.password)  # Inicia sesión
        self.post = Post.objects.create(user=self.user, body='This is a test post.')  # Crear una publicación

    def test_like_post(self):
        # Probar que un usuario puede dar "me gusta" a una publicación
        response = self.client.post(reverse('like_post', args=[self.post.id]))  # Suponiendo que tienes una vista de "like_post"
        self.assertEqual(response.status_code, 200)  # Verifica que la respuesta sea correcta
        self.post.refresh_from_db()  # Actualiza la instancia del modelo
        self.assertTrue(self.post.is_liked)  # Verifica que la publicación ahora está marcada como "me gusta"
        self.assertEqual(self.post.likes.count(), 1)  # Verifica que el conteo de "me gusta" sea 1

    def test_unlike_post(self):
        # Probar que un usuario puede eliminar su "me gusta" de una publicación
        self.post.likes.add(self.user)  # Agrega "me gusta" a la publicación
        response = self.client.post(reverse('like_post', args=[self.post.id]))  # Vuelve a hacer la misma acción para eliminarlo
        self.assertEqual(response.status_code, 200)  # Verifica que la respuesta sea correcta
        self.post.refresh_from_db()  # Actualiza la instancia del modelo
        self.assertFalse(self.post.is_liked)  # Verifica que la publicación ya no está marcada como "me gusta"
        self.assertEqual(self.post.likes.count(), 0)  # Verifica que el conteo de "me gusta" sea 0

    def test_like_post_not_authenticated(self):
        # Probar que un usuario no autenticado no puede dar "me gusta" a una publicación
        self.client.logout()  # Cerrar sesión
        response = self.client.post(reverse('like_post', args=[self.post.id]))
        self.assertEqual(response.status_code, 403)  # Debería devolver un estado 403 (Forbidden)

class ProfileTests(TestCase):

    def setUp(self):
        # Crear usuarios de prueba
        self.user1 = User.objects.create_user(username='user1', password='password1')
        self.user2 = User.objects.create_user(username='user2', password='password2')
        
        # Seguir al user1 para pruebas
        self.user1.profile.following.add(self.user2.profile)

    def test_view_profile(self):
        # Probar que la información del perfil del usuario se muestra correctamente
        self.client.login(username='user1', password='password1')
        response = self.client.get(reverse('profile', args=['user1']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'user1')  # Asegúrate de que el nombre de usuario aparece
        self.assertContains(response, 'Followers: 1')  # Asegúrate de que el número de seguidores es correcto
        self.assertContains(response, 'Following: 1')  # Asegúrate de que el número de seguidos es correcto

    def test_follow_user(self):
        # Probar que un usuario puede seguir a otro
        self.client.login(username='user1', password='password1')
        response = self.client.post(reverse('follow', args=['user2']))
        self.assertEqual(response.status_code, 302)  # Redirige después de seguir
        self.assertTrue(self.user1.following.filter(username='user2').exists())  # Verifica que ahora sigue a user2

    def test_unfollow_user(self):
        # Probar que un usuario puede dejar de seguir a otro
        self.client.login(username='user1', password='password1')
        self.client.post(reverse('unfollow', args=['user2']))  # Dejar de seguir a user2
        self.assertFalse(self.user1.following.filter(username='user2').exists())  # Verifica que ya no sigue a user2

    def test_following_count_updates(self):
        # Probar que la lista de seguidores y seguidos se actualiza correctamente
        self.client.login(username='user1', password='password1')

        # Antes de seguir
        response = self.client.get(reverse('profile', args=['user2']))
        self.assertContains(response, 'Followers: 0')  # Verifica que inicialmente user2 no tiene seguidores

        # Seguir a user2
        self.client.post(reverse('follow', args=['user2']))

        # Después de seguir
        response = self.client.get(reverse('profile', args=['user2']))
        self.assertContains(response, 'Followers: 1')  # Verifica que user2 ahora tiene un seguidor

        # Dejar de seguir
        self.client.post(reverse('unfollow', args=['user2']))

        # Después de dejar de seguir
        response = self.client.get(reverse('profile', args=['user2']))
        self.assertContains(response, 'Followers: 0')  # Verifica que user2 ya no tiene seguidores

class PaginationTests(TestCase):

    def setUp(self):
        # Crear usuarios de prueba
        self.user = User.objects.create_user(username='testuser', password='password123')
        
        # Crear publicaciones de prueba
        for i in range(15):  # Crear 15 publicaciones para probar la paginación
            Post.objects.create(user=self.user, body=f'Post {i+1}')

    def test_pagination_on_index(self):
        # Probar la paginación en la página principal (índice)
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('index') + '?page=1')  # Primera página
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Post 1')  # Verifica que el primer post esté en la primera página
        self.assertContains(response, 'Post 10')  # Verifica que el décimo post esté en la primera página
        self.assertNotContains(response, 'Post 11')  # Verifica que el undécimo post no esté en la primera página

    def test_pagination_on_profile(self):
        # Probar la paginación en el perfil del usuario
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('profile', args=['testuser']) + '?page=1')  # Primera página
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Post 1')  # Verifica que el primer post esté en la primera página del perfil
        self.assertContains(response, 'Post 10')  # Verifica que el décimo post esté en la primera página del perfil
        self.assertNotContains(response, 'Post 11')  # Verifica que el undécimo post no esté en la primera página del perfil

    def test_pagination_next_page(self):
        # Probar que se puede acceder a la siguiente página
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('index') + '?page=2')  # Segunda página
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Post 11')  # Verifica que el undécimo post esté en la segunda página
        self.assertContains(response, 'Post 15')  # Verifica que el decimoquinto post esté en la segunda página
        self.assertNotContains(response, 'Post 1')  # Verifica que el primer post no esté en la segunda página

class ServerResponseTests(TestCase):

    def setUp(self):
        # Crear un usuario de prueba
        self.user = User.objects.create_user(username='testuser', password='password123')

    def test_index_page_response(self):
        # Verificar que la página de índice devuelva un código de estado 200
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_login_page_response(self):
        # Verificar que la página de inicio de sesión devuelva un código de estado 200
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_register_page_response(self):
        # Verificar que la página de registro devuelva un código de estado 200
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_profile_page_response(self):
        # Verificar que la página de perfil devuelva un código de estado 200 para usuarios autenticados
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('profile', args=['testuser']))
        self.assertEqual(response.status_code, 200)

    def test_protected_page_response(self):
        # Verificar que la página de perfil devuelva un código de estado 403 para usuarios no autenticados
        response = self.client.get(reverse('profile', args=['testuser']))
        self.assertEqual(response.status_code, 403)

    def test_nonexistent_page_response(self):
        # Verificar que una página inexistente devuelva un código de estado 404
        response = self.client.get('/nonexistent-url/')
        self.assertEqual(response.status_code, 404)

class SecurityTests(TestCase):

    def setUp(self):
        # Crear usuarios de prueba
        self.admin_user = User.objects.create_superuser(username='admin', password='adminpass', email='admin@example.com')
        self.regular_user = User.objects.create_user(username='regularuser', password='userpass')

    def test_admin_page_access(self):
        # Verificar que la página de administración no sea accesible para un usuario regular
        self.client.login(username='regularuser', password='userpass')
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 403)  # Debe ser 403 Forbidden

    def test_admin_page_access_as_admin(self):
        # Verificar que la página de administración sea accesible para el usuario administrador
        self.client.login(username='admin', password='adminpass')
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)  # Debe ser 200 OK

    def test_user_data_access(self):
        # Crear un perfil de usuario
        profile = Profile.objects.create(user=self.regular_user)

        # Intentar acceder al perfil de otro usuario sin permisos
        self.client.login(username='regularuser', password='userpass')
        response = self.client.get(reverse('profile', args=['admin']))  # Asumiendo que el admin tiene un perfil
        self.assertEqual(response.status_code, 403)  # Debe ser 403 Forbidden

    def test_access_own_profile(self):
        # Acceder al perfil del propio usuario
        self.client.login(username='regularuser', password='userpass')
        response = self.client.get(reverse('profile', args=['regularuser']))
        self.assertEqual(response.status_code, 200)  # Debe ser 200 OK

class StyleAndDesignTests(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Configuración del controlador de Chrome
        cls.browser = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()

    def test_elements_display_correctly_on_mobile(self):
        self.browser.get(self.live_server_url + '/')
        self.browser.set_window_size(375, 667)  # Tamaño de pantalla de un móvil

        # Verifica que el título principal se muestre
        title = self.browser.find_element(By.CLASS_NAME, 'principal-title')
        self.assertEqual(title.text, 'Social Network')  # Cambia esto según tu título real

        # Verifica que la barra de navegación esté presente
        nav = self.browser.find_element(By.CLASS_NAME, 'layout-buttons')
        self.assertIsNotNone(nav)

        # Verifica que los botones de navegación sean accesibles
        buttons = self.browser.find_elements(By.CSS_SELECTOR, '.layout-item-button a')
        self.assertGreater(len(buttons), 0)

    def test_elements_display_correctly_on_desktop(self):
        self.browser.get(self.live_server_url + '/')
        self.browser.set_window_size(1280, 800)  # Tamaño de pantalla de un escritorio

        # Verifica que el título principal se muestre
        title = self.browser.find_element(By.CLASS_NAME, 'principal-title')
        self.assertEqual(title.text, 'Social Network')  # Cambia esto según tu título real

        # Verifica que la barra de navegación esté presente
        nav = self.browser.find_element(By.CLASS_NAME, 'layout-buttons')
        self.assertIsNotNone(nav)

        # Verifica que los botones de navegación sean accesibles
        buttons = self.browser.find_elements(By.CSS_SELECTOR, '.layout-item-button a')
        self.assertGreater(len(buttons), 0)

    def test_no_style_errors(self):
        self.browser.get(self.live_server_url + '/')

        # Este test puede ser más específico dependiendo de lo que consideres un "error de estilo".
        # Aquí solo verificamos que no haya errores en la consola de JavaScript.
        logs = self.browser.get_log('browser')
        for entry in logs:
            if 'SEVERE' in entry['level']:
                self.fail("JavaScript errors found in console: {}".format(entry['message']))

class JavaScriptTests(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.browser = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()

    def test_like_functionality(self):
        # Asume que el usuario está autenticado y ha publicado al menos un post
        self.browser.get(self.live_server_url + '/')
        time.sleep(1)  # Esperar a que la página cargue

        # Localizar el botón "Like" para el primer post
        like_button = self.browser.find_element(By.ID, 'like-post-button-1')  # Cambia el ID según tu lógica
        like_button.click()
        time.sleep(1)  # Esperar a que la acción se procese

        # Verificar que el botón cambie a "Unlike"
        self.assertEqual(like_button.text, "Unlike")

        # Verificar que el conteo de "likes" se haya incrementado
        likes_count = self.browser.find_element(By.ID, 'likes-count-1')  # Cambia el ID según tu lógica
        self.assertIn("Like", likes_count.text)  # Asegúrate de que el texto sea correcto

    def test_follow_functionality(self):
        self.browser.get(self.live_server_url + '/profile/someuser/')  # Cambia según el perfil a probar
        time.sleep(1)

        follow_button = self.browser.find_element(By.ID, 'follow-button')  # Cambia el ID según tu lógica
        follow_button.click()
        time.sleep(1)

        # Verificar que el botón cambie a "Unfollow"
        self.assertEqual(follow_button.text, "Unfollow")

    def test_error_message_display(self):
        self.browser.get(self.live_server_url + '/login/')
        time.sleep(1)

        # Intenta iniciar sesión con credenciales incorrectas
        username_input = self.browser.find_element(By.NAME, 'username')
        password_input = self.browser.find_element(By.NAME, 'password')
        username_input.send_keys('wronguser')
        password_input.send_keys('wrongpass')
        
        login_button = self.browser.find_element(By.CSS_SELECTOR, 'input[type="submit"]')
        login_button.click()
        time.sleep(1)

        # Verifica que se muestre el mensaje de error
        error_message = self.browser.find_element(By.CLASS_NAME, 'error-message')  # Cambia según tu clase de error
        self.assertIn("Invalid credentials", error_message.text)  # Asegúrate de que el texto sea correcto
