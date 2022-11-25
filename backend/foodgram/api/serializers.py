from rest_framework import serializers

from users.models import User

from .validators import UserDataValidator


class UserSerializer(serializers.ModelSerializer, UserDataValidator):
    '''Сериализация данных пользователя.'''

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'password')
        read_only_fields = ('id', 'is_subscribed')
