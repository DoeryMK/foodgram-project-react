from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from djoser.serializers import UserSerializer

from users.models import User

from .validators import UserDataValidator


class SpecialUserSerializer(UserSerializer):
    is_subscribed = serializers.BooleanField(default=False) # Поменять на отношение (поле модели Follow)
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed')
        read_only_fields = ('email', 'id', 'username', 'first_name', 'last_name')









#
# class UserSerializer(serializers.ModelSerializer):
#     """Сериализация данных пользователя."""
#     username = serializers.CharField(required=True, read_only=True)
#
#     class Meta:
#         model = User
#         fields = ('email', 'id', 'username', 'first_name',
#                   'last_name', 'is_subscribed')
#
#
# class UserIdSerializer(UserSerializer):
#     """Сериализация данных пользователя."""
#     id = serializers.BooleanField(required=True, )
#
# class SignupSerializer(serializers.ModelSerializer, UserDataValidator):
#     """Сериализация данных пользователя при регистрации."""
#
#     class Meta:
#         model = User
#         fields = ('id', 'username', 'email', 'first_name',
#                   'last_name', 'password')
#         read_only_fields = ('id',)
#         write_only_fields = ('password', )
#
# class PasswordSerializer(serializers.ModelSerializer):
#     """Сериализация данных пользователя при смене пароля."""
#     # new_password = serializers.HiddenField(
#     #     default=serializers.CurrentUserDefault(), source='password')
#     # current_password = serializers.HiddenField(
#     #     default=serializers.CurrentUserDefault(), source='password')
#     new_password = serializers.CharField(write_only=True, required=True,
#                                          validators=[validate_password])
#     current_password = serializers.CharField(write_only=True, required=True,
#                                              source='password')
#     class Meta:
#         model = User
#         fields = ('new_password', 'current_password')
#
#     def validator(self, data):
#         """Проверка корректного ввода данных."""
#         user = self.context['request'].user
#         if data['current_password'] != user.password:
#             raise serializers.ValidationError(
#                 'Введен некорректный текущий пароль')
#         if data['new_password'] == data['current_password']:
#             raise serializers.ValidationError(
#                 'Пароли совпадают. Придумайте новый пароль')
#         return data
#
#     # def validate_new_password(self, value):
#     #     try:
#     #         validate_password(value)
#     #     except Exception:
#     #         raise serializers.ValidationError(
#     #             'Введен некорректный new_password')
#     #     return value

