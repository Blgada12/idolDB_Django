from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('all/', views.idol_all, name='idolAll'),
    path('detail/<int:idol_id>', views.idol_detail, name='idolDetail'),
    path('', views.idol_main, name='idolMain')
]
