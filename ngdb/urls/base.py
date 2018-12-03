from django.urls import path, include

urlpatterns = [
    path('', include('idolmaster.urls')),
    path('api-auth/', include('rest_framework.urls'))
]

