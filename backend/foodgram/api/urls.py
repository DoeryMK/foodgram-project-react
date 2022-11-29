from django.urls import include, path
from rest_framework import routers

# from .views import UserViewSet

auth_urls = [
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]

#router_v1 = routers.DefaultRouter()
#router_v1.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    #path('v1/', include(router_v1.urls)),
    path(r'v1/', include(auth_urls)),
]