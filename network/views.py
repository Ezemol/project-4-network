from django.contrib.auth.decorators import login_required  # Decorador para requerir inicio de sesión
from django.views.decorators.csrf import csrf_exempt  # Decorador para permitir solicitudes POST sin CSRF
from django.contrib.auth import authenticate, login, logout  # Funciones para autenticar y manejar sesiones de usuario
from django.db import IntegrityError  # Manejo de errores de integridad en la base de datos
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse  # Respuestas HTTP
from django.shortcuts import render, get_object_or_404  # Funciones para renderizar vistas y obtener objetos
from django.urls import reverse  # Función para generar URLs
import json  # Módulo para manejar JSON

from .models import User, Post, Profile  # Importar modelos necesarios


def index(request):
    # Obtener todos los posts activos ordenados por fecha
    active_posts = Post.objects.filter(is_active=True).order_by('-timestamp')

    # Renderizar la vista del índice con los posts activos
    return render(request, "network/index.html", {
        "active_posts": active_posts
    })


def login_view(request):
    if request.method == "POST":
        # Intentar iniciar sesión
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Verificar si la autenticación fue exitosa
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))  # Redirigir al índice
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."  # Mensaje de error
            })
    else:
        return render(request, "network/login.html")  # Renderizar la vista de inicio de sesión


def logout_view(request):
    logout(request)  # Cerrar sesión
    return HttpResponseRedirect(reverse("index"))  # Redirigir al índice


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Asegurarse de que la contraseña coincide con la confirmación
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."  # Mensaje de error
            })

        # Intentar crear un nuevo usuario
        try:
            user = User.objects.create_user(username, email, password)
            user.save()  # Guardar el usuario en la base de datos
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."  # Mensaje de error
            })
        login(request, user)  # Iniciar sesión con el nuevo usuario
        return HttpResponseRedirect(reverse("index"))  # Redirigir al índice
    else:
        return render(request, "network/register.html")  # Renderizar la vista de registro

# Crear un nuevo post
@login_required
def new_post(request):
    if request.method == "POST":
        # Crear un nuevo post hecho por el usuario
        post_made = request.POST["post_made"]

        # Si el post no está vacío
        if post_made is not None:
            # Guardar datos del nuevo post
            post = Post(
                user=request.user,
                body=post_made
            )
            post.save()  # Guardar el post en la base de datos
            return HttpResponseRedirect(reverse("index"))  # Redirigir al índice
        # Si el post está vacío devolver error
        return render(request, "network/new_post.html", {
            "message": "You can't post an empty text."  # Mensaje de error
        })
    else:
        return render(request, "network/new_post.html")  # Renderizar la vista para crear un nuevo post
    
def profile(request, username):
    # Obtener el usuario en la base de datos
    user = get_object_or_404(User, username=username)
    # Buscar el perfil del usuario
    profile, created = Profile.objects.get_or_create(user=user)

    # Obtener todos los posts del dueño del perfil
    posts = Post.objects.filter(user=user).order_by("-timestamp")

    # Inicializar variables
    is_following = False
    is_profile = False
    num_followers = profile.followers.count()  # Contar seguidores
    num_following = user.following.count()  # Contar seguidos

    # Si es el perfil del usuario, no mostrar la opción de seguir
    if request.user == user:
        is_profile = True 

    # Verificar si el usuario está siguiendo al dueño del perfil
    if request.user.is_authenticated and not is_profile:
        is_following = request.user in profile.followers.all()
        
    return render(request, "network/profile.html", {
            "profile_user": user,
            "profile": profile,
            "posts": posts,
            "is_following": is_following,
            "num_followers": num_followers,
            "num_following": num_following,
            "is_profile": is_profile,
        })

    
# Función para seguir/dejar de seguir usuarios
@csrf_exempt
@login_required
def follow_user(request, profile_id):
    if request.method == 'POST':
        if request.user.is_authenticated:
            try: 
                user_to_follow = get_object_or_404(User, pk=profile_id)  # Obtener el usuario a seguir

                profile = user_to_follow.profile  # Obtener el perfil del usuario

                # Verificar si el usuario ya sigue al perfil
                if request.user in profile.followers.all():
                    profile.followers.remove(request.user)  # Dejar de seguir
                    is_following = False
                else:
                    profile.followers.add(request.user)  # Seguir
                    is_following = True

                return JsonResponse({
                    "message": "success",
                    "is_following": is_following  # Retornar el estado de seguimiento
                }, status=200)
            except User.DoesNotExist:
                return JsonResponse({"error": "User not found."}, status=404)  # Manejar usuario no encontrado
        else:
            return JsonResponse({"error": "The user is not authenticated"}, status=403)  # Manejar usuario no autenticado
    return JsonResponse({"error": "POST request required."}, status=400)  # Manejar método incorrecto