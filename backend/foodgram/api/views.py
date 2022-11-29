from djoser.permissions import CurrentUserOrAdmin
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from djoser.views import UserViewSet

from users.models import User

from .paginator import CustomPagination
from .serializers import SpecialUserSerializer



class SpecialUserViewSet(UserViewSet):
    """Обработка запросов к данным пользователей.
    Эндпоинты: "users/", "users/id/", "users/me/", "users/set_password/"
    "users/subscriptions/", "users/id/subscribe/"."""
    serializer_class = SpecialUserSerializer
    queryset = User.objects.all()
    # pagination_class = CustomPagination

    # @action(methods=['get'], detail=False,)
    # def me(self, request, pk=None):
    #     user = User.objects.get(username=request.user.username)
    #     serializer = self.serializer_class(user)
    #     return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True,
            permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        pass

    @action(methods=['post'], detail=False,
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, pk=None):
        pass
