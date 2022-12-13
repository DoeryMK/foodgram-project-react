from django.urls import include, path, re_path
from rest_framework import routers

# from .views import UserViewSet
from .views import SpecialUserViewSet

auth_urls = [
    path('auth/', include('djoser.urls.authtoken')),
]

router_v1 = routers.DefaultRouter()
router_v1.register(r'users', SpecialUserViewSet, basename='users')

urlpatterns = [
    path('', include(router_v1.urls)),
    path(r'', include(auth_urls)),
]