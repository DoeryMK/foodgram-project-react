from django.urls import include, path, re_path
from rest_framework import routers

# from .views import UserViewSet
from .views import SpecialUserViewSet

auth_urls = [
    # path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]

router_v1 = routers.DefaultRouter()
router_v1.register(r'users', SpecialUserViewSet, basename='users')
# router_v1.register(
#     r'users/(?P<pk>[^/.]+)/subscribe',
#     SpecialUserViewSet, basename='subscribe')

urlpatterns = [
    # re_path(r'^users\/(?P<pk>[^/.]+)\/subscribe', FollowViewSet.as_view(
    #     {'post': 'create', 'delete': 'destroy'})),
    path('', include(router_v1.urls)),

    path(r'', include(auth_urls)),
]