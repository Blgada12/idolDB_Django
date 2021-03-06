from django.contrib import admin
from django.urls import path, re_path
from . import views

from django.conf.urls import url, include
from rest_framework import routers


urlpatterns = [
    path('signup', views.Register.as_view(), name='signup'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
]
