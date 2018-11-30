from django.contrib import admin
from django.urls import path,re_path
from . import views

urlpatterns = [
    path('all/', views.idol_all, name='idolAll'),
    path('detail/<int:idol_id>', views.idol_detail, name='idolDetail'),
    path('', views.idol_main, name='idolMain'),
    path('search/', views.idol_search, name='idolSearch'),
    path('search/<str:value>', views.idol_search, name='idolSearch'),
    path('signup', views.register, name='signup'),
    path('activate/<str:uid>/<str:token>', views.email_activate, name='activate'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('camelog/', views.cameLog, name='cameLog')
]
