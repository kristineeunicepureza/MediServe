# MediServe/urls.py (Project Level)

from django.contrib import admin
from django.urls import path, include
from django.conf import settings # <-- ADDED
from django.conf.urls.static import static # <-- ADDED

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]

# This is essential for serving media files (user uploads) during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # <-- ADDED