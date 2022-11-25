from django.urls import include, path
from rest_framework import routers

from .views import UserViewSet

auth_urls = []

router_v1 = routers.DefaultRouter()
router_v1.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/', include(auth_urls))
]