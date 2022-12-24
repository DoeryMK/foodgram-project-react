from django.urls import include, path
from rest_framework import routers

from .views import (IngredientViewSet, RecipesViewSet, SpecialUserViewSet,
                    TagViewSet)

auth_urls = [
    path('auth/', include('djoser.urls.authtoken')),
]

router_v1 = routers.DefaultRouter()
router_v1.register(r'users', SpecialUserViewSet, basename='users')
router_v1.register(r'tags', TagViewSet, basename='tags')
router_v1.register(r'ingredients', IngredientViewSet, basename='tags')
router_v1.register(r'recipes', RecipesViewSet, basename='recipes')

urlpatterns = [
    path('', include(router_v1.urls)),
    path(r'', include(auth_urls)),
]
