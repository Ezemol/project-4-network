from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from .models import User, Post, Profile


def index(request):
    active_posts = Post.objects.filter(is_active=True).order_by('-timestamp')

    return render(request, "network/index.html", {
        "active_posts":active_posts
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

# Crear post nuevo
def new_post(request):
    if (request.method == "POST"):
        # Post nuevo hecho por el user
        post_made = request.POST["post_made"]

        # If post no está vacío
        if (post_made is not None):
            # Guardar datos del nuevo post
            post = Post(
                user=request.user,
                body=post_made
                )
            post.save()
            return HttpResponseRedirect(reverse("index"))
        # If post está vacío devuelvo error
        return render(request, "network/new_post.html", {
            "message":"You can't post an empty text."
        })
    else:
        return render(request, "network/new_post.html")
    
def profile(request, username):
    # Get user en la base de datos
    user = get_object_or_404(User, username=username)
    # Buscar el perfil del usuario
    profile, created = Profile.objects.get_or_create(user=user)

    # Get todos los posts del dueño de perfil
    posts = Post.objects.filter(user=user).order_by("-timestamp")

    # Inicio variables
    is_following = False
    is_profile = False
    num_followers = profile.followers.count()
    num_following = user.following.count()

    # If es el perfil del user no muestra el seguir
    if request.user == user:
        is_profile = True 

    # Verifico si el usuario está siguiendo al dueño del perfil
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

    
# Funcion para follow/unfollow usuarios
def follow_user(request):
    # TODO
    pass
