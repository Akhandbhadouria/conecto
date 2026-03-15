"""
URL configuration for tax_fare_django project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static 
from . import views
from django.urls import path
from django.contrib.auth.views import LogoutView

urlpatterns = [
     path("", views.home, name="home"),

     path("tweet/", views.tweet_list, name="tweet_list"),
    path("create/", views.tweet_create, name="tweet_create"),
    path("<int:tweet_id>/edit/", views.tweet_edit, name="tweet_edit"),
    path("<int:tweet_id>/delete/", views.tweet_delete, name="tweet_delete"),
    path("register/", views.register, name="register"),
    path("logout/", LogoutView.as_view(next_page='/'), name="logout"),

    path("<int:tweet_id>/like/", views.like_tweet, name="like_tweet"),  # NEW

    path('create-profile/', views.create_profile, name='create_profile'),
    path('profile/<str:username>/follow/', views.follow_user, name='follow_user'),
    path('profile/<str:username>/followers/', views.followers_list, name='followers_list'),
    path('profile/<str:username>/following/', views.following_list, name='following_list'),
    path('my-feed/', views.my_feed, name='my_feed'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path("search/", views.search_user, name="search"),
path("delete-account/", views.delete_account, name="delete_account"),

    path('following-feed/', views.following_feed, name='following_feed'),
    path('profile/<str:username>/', views.profile_detail, name='profile_detail'),

    path("account-settings/", views.account_settings, name="account_settings"),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)