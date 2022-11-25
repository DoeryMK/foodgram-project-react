from rest_framework import viewsets

from .serializers import UserSerializer

from users.models import User


class UserViewSet(viewsets.ModelViewSet):
    """Обработка запросов к данным пользователей."""
    serializer_class = UserSerializer
    queryset = User.objects.all()
