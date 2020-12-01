import debug_toolbar
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include

from rest_framework.routers import SimpleRouter

from shop.views import BookViewSet, auth, UserBookRelationView

router = SimpleRouter()
router.register(r'book', BookViewSet)
router.register(r'book_relation', UserBookRelationView)

urlpatterns = [
    path('admin/', admin.site.urls),
    url('', include('social_django.urls', namespace='social')),
    path('auth/', auth),
    path('__debug__/', include(debug_toolbar.urls)),
]

urlpatterns += router.urls
