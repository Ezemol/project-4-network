from django.contrib.auth import get_user_model
from django.db.models import Max
from django.test import Client, TestCase
from .models import Profile, Post

#TODO
#TODO

User = get_user_model()

class Test_program(TestCase):

    def setUp(self):
        # Crear un usuario y su perfil
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="1234")
        self.profile = Profile.objects.create(user=self.user)

        # Crear post
        self.post = Post.objects.create(user=self.user, body="This is a test 1.")

    def test_user_registration(self):
        """" Revisa si el usuario se registra correctamente """
        response = self.client.post('register', {
            'username': 'newuser', 
            'email': 'newuser@email.com',
            'password': '1234',
            'confirmation': '1234',
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_correct(self):
        """ Revisa si el usuario se loguea correctamente """
        response = self.client.post('login', {
            'username': 'testuser',
            'password':'1234'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.wsgi_request.user, self.user)


    def test_new_post_creation(self):
        """ Revisa si se realiza un post correctamente """
        self.client.login(username="testuser", password="1234")
        response = self.client.post("new post", {
            'post_made':'Another post.'
        })

        self.assertEqual(response.status_code, 200)
 
    def test_profile_view(self):
        """ Verifica que  """
        pass