from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [

    path('', views.index),
    path('register/', views.registerPage),

    path('api/register/', views.register),
    path('api/registerVerify/', views.registerVerify),

    path('api/validate/', views.validateContact),
    path('api/signin/', views.signin),
    path("logout/", views.logout_view),
    
]