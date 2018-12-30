from django.contrib import admin
from django.urls import path, re_path
from . import views

from django.conf.urls import url, include
from rest_framework import routers


urlpatterns = [
    path('camelog/', views.CameLogView.as_view(), name='cameLog'),
]
