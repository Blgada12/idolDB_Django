from .base import *

from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from rest_framework_swagger.views import get_swagger_view

urlpatterns.append(path('admin/', admin.site.urls))

schema_view = get_swagger_view(title="My API")
urlpatterns.append(path('api/swagger', schema_view))
urlpatterns.append(path('api-auth/', include('rest_framework.urls')))

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
