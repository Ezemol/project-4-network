from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_post", views.new_post, name="new_post"),
    path("following_posts", views.following_posts, name="following_posts"),

    # API routes
    path('profile/<str:username>/', views.profile, name='profile'),
    path('follow/<int:profile_id>/', views.follow_user, name='follow_user'),
    path('edit_post/<int:post_id>/', views.edit_post, name="edit_post"),
    path('like_post/<int:post_id>/', views.like_post, name="like_post"),
    path("profile_connections/<int:profile_id>/", views.profile_connections, name="profile_connections"),

]
