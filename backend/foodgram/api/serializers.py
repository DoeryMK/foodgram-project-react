from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework.validators import UniqueTogetherValidator



from .validators import UserDataValidator
from users.models import Follow, User


class SignUpSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'password')
        read_only_fields = ('id', )


class SpecialUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        return True

class RecipesSerializer(serializers.ModelSerializer):
    pass

class SubscribeSerializer(serializers.ModelSerializer):
    # authors = SpecialUserSerializer(many=True, read_only=True)
    # email = serializers.EmailField(read_only=True)
    recipes = RecipesSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField(default=0)
    is_subscribed = serializers.SerializerMethodField()
    # username = serializers.SlugRelatedField(
    #     queryset=User.objects.all(), slug_field='username', required=False)
    # user = serializers.SlugRelatedField(
    #     read_only=True, slug_field='username',
    #     default=serializers.CurrentUserDefault())


    class Meta:
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')
        model = User
        read_only_fields = ('email', 'first_name', 'last_name')

    # def validate_following(self, value):
    #     if value == self.context.get("request").user:
    #         raise serializers.ValidationError(
    #             'Подписка на самого себя запрещена')
    #     return value

    def create(self, validate_data):
        user = self.context.get("request").user
        author = User.objects.get(id=self.context['view'].kwargs.get('id'))
        return Follow.objects.create(user=user, author=author)

    def get_is_subscribed(self, obj):
        return True
    #     request = self.context.get("request")
    #     if request and hasattr(request, "user"):
    #         user = request.user
    #     else:
    #         return False
    #     author = User.objects.get(id=self.context['view'].kwargs.get('id'))
    #     return Follow.objects.filter(user=user, author=author).exists()

    def get_recipes_count(self, obj):
        # пересчитывать один раз в момент новой подписки на пользователя?
        # Но данные тогда могут быть не актуальными
        pass




