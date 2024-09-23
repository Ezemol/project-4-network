from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_post", views.new_post, name="new_post"),
    path("following", views.following, name="following"),

    # API routes
    path('profile/<str:username>/', views.profile, name='profile'),
    path('follow/<int:profile_id>/', views.follow_user, name='follow_user'),
    path('edit_post/<int:post_id>/', views.edit_post, name="edit_post"),

]
