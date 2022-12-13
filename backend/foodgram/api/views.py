from django.shortcuts import get_object_or_404
from djoser.permissions import CurrentUserOrAdmin
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from djoser.views import UserViewSet

from users.models import User

from .paginator import CustomPagination
from .serializers import SpecialUserSerializer, SubscribeSerializer
from users.models import Follow


class SpecialUserViewSet(UserViewSet):
    """Обработка запросов к данным пользователей.
    Эндпоинты: "users/", "users/id/", "users/me/", "users/set_password/"
    "users/subscriptions/", "users/id/subscribe/"."""
    serializer_class = SpecialUserSerializer
    queryset = User.objects.all()
    # http_method_names = ['get', 'post', 'delete'] # Такое ограничение не работает!
    # pagination_class = CustomPagination

    # Такое ограничение не работает!
    # def partial_update(self, request, *args, **kwargs):
    #     raise MethodNotAllowed("PATCH")
    #
    # # Такое ограничение не работает!
    # def update(self, request, *args, **kwargs):
    #     raise MethodNotAllowed("PUT")

    # @action(methods=['get'], detail=False,
    #         permission_classes=(IsAuthenticated,))
    # def subscriptions(self, request):
    #     following = self.request.user.subscriber.all()
    #     serializer = SubscribeSerializer(following)
    #     return Response(serializer.data, status=status.HTTP_200_OK)
    #
    # @action(methods=['post', 'delete'], detail=True,
    #         url_name='subscribe',
    #         url_path='subscribe',
    #         serializer_class=SubscribeSerializer,
    #         permission_classes=(IsAuthenticated,))
    # def subscribe(self, request, pk):
    #     serializer = SubscribeSerializer(data=request.data)
    #     # author = get_object_or_404(User, id=pk)
    #     user = self.request.user
    #     if request.method == 'POST':
    #         author = get_object_or_404(User, id=serializer.validated_data['id'])
    #
    #         serializer.is_valid(raise_exception=True)
    #         # Follow.objects.create(user=user, author=author)
    #         serializer.save(Follow, user=self.request.user, author=author)
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     elif request.method == 'DELETE':
    #         author = serializer.validated_data['id']
    #         # user = self.request.user
    #         follow = get_object_or_404(Follow, author=author, user=user)
    #         follow.delete()
    #         # serializer.delete(user=self.request.user)
    #         return Response(status=status.HTTP_204_NO_CONTENT)
    #     else:
    #         return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


# class FollowViewSet(viewsets.ModelViewSet):
#     serializer_class = SubscribeSerializer
#     permission_classes = (IsAuthenticated,)
    #
    # def perform_create(self, serializer):
    #     serializer.save(user=self.request.user)
    #
    # @action(methods=['post', 'delete'], detail=False,
    #         url_name='subscribe',
    #         url_path='subscribe',
    #         permission_classes=(IsAuthenticated,))
    # def subscribe(self, request, pk):
    #     serializer = self.serializer_class(data=request.data)
    #     if request.method == 'POST':
    #         author = get_object_or_404(User, id=serializer.validated_data['id'])
    #         serializer.is_valid(raise_exception=True)
    #         serializer.save(Follow, user=self.request.user, author=author)
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     elif request.method == 'DELETE':
    #         author = serializer.validated_data['id']
    #         user = self.request.user
    #         get_object_or_404(Follow, author=author, user=user)
    #         serializer.delete(user=self.request.user)
    #         return Response(status=status.HTTP_204_NO_CONTENT)
    #     else:
    #         return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)