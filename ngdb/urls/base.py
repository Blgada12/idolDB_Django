from django.urls import path, include


urlpatterns = [
    path('', include('idolmaster.urls')),
    path('account/', include('users.urls')),
]

