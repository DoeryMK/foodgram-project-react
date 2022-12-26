from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import Follow, User
from .custom_render import PlainTextRenderer
from .paginator import CustomPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (IngredientSerializer, RecipesSerializer,
                          ShortRecipeSerializer, RegisteredUserSerializer,
                          SubscribeSerializer, TagSerializer)


class SpecialUserViewSet(UserViewSet):
    """Вьюсет обработки эндпоинтов к данным пользователей."""

    serializer_class = RegisteredUserSerializer
    queryset = User.objects.all()
    http_method_names = ('get', 'post', 'delete')
    pagination_class = CustomPagination

    @action(methods=('get',), detail=False,
            permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        authors_queryset = list(
            User.objects.filter(
                authors__user=request.user
            )
        )
        page = self.paginate_queryset(authors_queryset)
        if page:
            serializer = SubscribeSerializer(
                page, many=True, context={'request': request}
            )
            return self.get_paginated_response(
                serializer.data
            )
        serializer = SubscribeSerializer(
            authors_queryset, many=True, context={'request': request}
        )
        return Response(
            serializer.data, status=status.HTTP_200_OK
        )

    @action(methods=('post', 'delete'),
            detail=True,
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, id):
        author = get_object_or_404(
            User, id=id
        )
        if request.method == 'POST':
            serializer = SubscribeSerializer(
                author, context={'request': request}
            )
            if request.user == author:
                return JsonResponse(
                    {'errors': "Подписка на самого себя запрещена"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            try:
                Follow.objects.create(
                    user=request.user, author=author
                )
            except IntegrityError:
                return JsonResponse(
                    {'errors': "Пользователь уже подписан на автора."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )

        elif request.method == 'DELETE':
            try:
                follow = Follow.objects.get(
                    user=request.user, author=author
                )
            except ObjectDoesNotExist:
                return JsonResponse(
                    {'errors': "Невозможно отписать от автора, "
                     "на которого не подписан."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            follow.delete()
            return Response(
                status=status.HTTP_204_NO_CONTENT
            )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет обработки эндпоинтов к данным тегов."""

    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет обработки эндпоинтов к данным ингридиентов."""

    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    pagination_class = None
    filter_backends = (SearchFilter,)
    search_fields = ('^name',)


class RecipesViewSet(viewsets.ModelViewSet):
    """Вьюсет обработки эндпоинтов, связанных с рецептами."""

    serializer_class = RecipesSerializer
    http_method_names = ('get', 'post', 'patch', 'delete')
    pagination_class = CustomPagination
    filter_backends = (filters.OrderingFilter,)
    ordering = ('-pub_date',)
    permission_classes = (IsAuthorOrReadOnly,)


    def get_queryset(self):
        queryset = Recipe.objects.all()

        if self.request.user.is_anonymous:
            is_favorited, is_in_shopping_cart = False, False
        else:
            is_favorited = self.request.query_params.get('is_favorited')
            is_in_shopping_cart = self.request.query_params.get(
                'is_in_shopping_cart')

        if is_favorited:
            queryset = queryset.filter(
                favorite_recipes__owner=self.request.user
            ).all()
        if is_in_shopping_cart:
            queryset = queryset.filter(
                shoppingcart_recipes__owner=self.request.user
            ).all()
        author = self.request.query_params.get('author')
        if author:
            queryset = queryset.filter(
                author__id=author
            ).all()
        tags = self.request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(
                tags__slug__in=tags
            ).all()

        return queryset

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user
        )
        super().perform_create(
            serializer
        )

    def perform_update(self, serializer):
        serializer.save(
            author=self.request.user
        )
        super().perform_update(
            serializer
        )

    @action(methods=('get',),
            detail=False,
            permission_classes=(IsAuthenticated,),
            renderer_classes=(PlainTextRenderer,))
    def download_shopping_cart(self, request):
        if request.user.is_anonymous:
            return Response(
                status=status.HTTP_401_UNAUTHORIZED
            )
        recipes_query = Recipe.objects.filter(
            shoppingcart_recipes__owner=self.request.user
        ).all()

        ingredients_query = recipes_query.values(
            'ingredients_recipes__ingredient__name',
            'ingredients_recipes__ingredient__measurement_unit'
        ).annotate(
            amount=Sum('ingredients_recipes__amount')
        ).order_by()

        text = '\n'.join(
            [
                f"{item['ingredients_recipes__ingredient__name']}: "
                f"{item['amount']}, "
                f"{item['ingredients_recipes__ingredient__measurement_unit']}"
                for item in ingredients_query
            ]
        )
        filename = 'shopping_card.txt'
        response = HttpResponse(
            text, content_type='text/plain'
        )
        response['Content-Disposition'] = f"attachment'; filename={filename}"

        return response

    @action(methods=('post', 'delete'),
            detail=True)
    def favorite(self, request, pk):
        recipe = get_object_or_404(
            Recipe, pk=pk
        )
        serializer = ShortRecipeSerializer(
            recipe
        )
        if request.method == 'POST':
            try:
                Favorite.objects.create(
                    owner=request.user, recipe=recipe
                )
            except IntegrityError:
                return JsonResponse(
                    {'errors': "Рецепт уже добавлен в избранное."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        elif request.method == 'DELETE':
            try:
                favorite = Favorite.objects.get(
                    owner=request.user, recipe=recipe
                )
            except ObjectDoesNotExist:
                return JsonResponse(
                    {'errors': "Невозможно удалить рецепт не добавленный "
                               "в избранное."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            favorite.delete()
            return Response(
                status=status.HTTP_204_NO_CONTENT
            )

    @action(methods=('post', 'delete'),
            detail=True)
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(
            Recipe, pk=pk
        )
        serializer = ShortRecipeSerializer(
            recipe
        )
        if request.method == 'POST':
            try:
                ShoppingCart.objects.create(
                    owner=request.user, recipe=recipe
                )
            except IntegrityError:
                return JsonResponse(
                    {'errors': "Рецепт уже добавлен в избранное."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        elif request.method == 'DELETE':
            try:
                cart = ShoppingCart.objects.get(
                    owner=request.user, recipe=recipe
                )
            except ObjectDoesNotExist:
                return JsonResponse(
                    {'errors': "Невозможно удалить рецепт не добавленный "
                               "в избранное."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            cart.delete()
            return Response(
                status=status.HTTP_204_NO_CONTENT
            )
