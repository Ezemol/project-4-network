from django.contrib.auth.decorators import login_required  # Decorador para requerir inicio de sesión
from django.views.decorators.csrf import csrf_exempt  # Decorador para permitir solicitudes POST sin CSRF
from django.contrib.auth import authenticate, login, logout  # Funciones para autenticar y manejar sesiones de usuario
from django.db import IntegrityError  # Manejo de errores de integridad en la base de datos
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse  # Respuestas HTTP
from django.shortcuts import render, get_object_or_404  # Funciones para renderizar vistas y obtener objetos
from django.urls import reverse  # Función para generar URLs
import json  # Módulo para manejar JSON
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage # Crear páginas en el front

from .models import User, Post, Profile  # Importar modelos necesarios


def index(request):
    # Obtener todos los posts activos ordenados por fecha
    active_posts = Post.objects.filter(is_active=True).order_by('-timestamp')

    # Variable con las páginas y sus posts respectivos
    pagin = paginator(request, active_posts)

    # Renderizar la vista del índice con los posts activos
    return render(request, "network/index.html", {
        "active_posts": pagin["page_posts"],
        "title_page": "All posts",
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

    # Variable con las páginas y sus posts respectivos
    pagin = paginator(request, posts)

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
            "active_posts": pagin["page_posts"],
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


# Función para cargar página con posts de following people.
@login_required
def following(request):
    # Crear user variable
    user = request.user
    # Verificar si el usuario sigue a alguien
    if (user.following.count() > 0):
        # Obtener la lista de perfiles seguidos por el usuario
        following_profiles = user.following.all()

        # Crear un array con los usuarios que sigue
        following_users = [profile.user for profile in following_profiles]

        posts = Post.objects.all()

        # Filtrar los posts activos hechos por esos usuarios.
        active_posts = posts.filter(is_active=True, user__in=following_users).order_by("-timestamp")

        # Ver si ya likeó o no el post
        for post in posts:
            post.is_liked = post.likes.filter(id=request.user.id).exists()

        # Variable con las páginas y sus posts respectivos
        pagin = paginator(request, active_posts)
        
        # Renderizar página
        return render(request, "network/index.html", {
            "active_posts": pagin["page_posts"],
            "title_page": "Following Page",
            "posts": posts,
        })
    else:
        return render(request, "network/index.html", {
            "message": "You are currently not following anyone.",
            "title_page": "Following Page"
        })
    

# Creo función para hacer páginas
def paginator(request, posts):     
    # Creo página cada 10 posts
    paginator = Paginator(posts, 10)

    # Obtener la página en la que está el usuario o la primera como predeterminada
    page_num = request.GET.get('page', 1)

    try:
        # Intentar obtener la página solicitada
        page_posts = paginator.get_page(page_num)
    except PageNotAnInteger:
        # Si el número de página no es un numero entero, mostrar la primera página
        page_posts = paginator.page(1)
    except EmptyPage:
        # Si el número de página está fuera de rango, mostrar la última página disponible
        page_posts = paginator.page(paginator.num_pages)

    return {
        "page_posts": page_posts,
    }

@login_required
# Edit post view
def edit_post(request, post_id):
    if request.method == 'POST':
        try:
            # Obtener el contenido del post enviado
            data = json.loads(request.body)
            new_content = data.get('content')

            # Buscar el post en la base de datos y actualizar su contenido
            post = Post.objects.get(id=post_id)

            # Verifica si el usuario que hace la solicitud es el dueño del post.
            if post.user == request.user:
                post.body = new_content
                post.save()

                # Return éxito
                return JsonResponse({"success": True, "updatedContent": new_content})
            else:
                # Devuelve error
                return JsonResponse({"error": "You don't have permission to edit this post."}, status=403)
        except Post.DoesNotExist:
            return JsonResponse({"error": "Post not found."}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Método no permitido."}, status=405)
    

@login_required
# Like / dislike post view
def like_post(request, post_id):
    if request.method == 'POST':
        try:
            # Obtener el contenido del post enviado
            data = json.loads(request.body)
            is_liked = data.get('isLiked')  

            # Buscar en la base de datos el post   
            post = Post.objects.get(id=post_id)

            # Actualizar base de datos
            if is_liked == True:
                post.like(request.user)
            else:
                post.dislike(request.user)
            post.save()
            
            return JsonResponse({"success": True, "isLiked": is_liked})
        
        except Post.DoesNotExist:
            return JsonResponse({"error": "Post not found."}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({'error': "Method not allowed."}, status=405)