from django.contrib import admin
from django.urls import path, re_path
from . import views

from django.conf.urls import url, include
from rest_framework import routers

router = routers.DefaultRouter()
router.register('idols', views.IdolViewSet)

urlpatterns = [

    path('all/', views.idolAll.as_view(), name='idolAll'),
    path('detail/<int:idol_id>', views.idolDetail.as_view(), name='idolDetail'),
    path('', views.idolMain.as_view(), name='idolMain'),
    path('search/', views.idolSearch.as_view(), name='idolSearch'),
    path('search/<str:value>', views.idolSearch.as_view(), name='idolSearch'),

    path('api/', include(router.urls))
]
