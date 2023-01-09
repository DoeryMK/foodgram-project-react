from django.core.validators import MinValueValidator
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.pagination import _positive_int

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import Follow, User


class SignUpSerializer(UserCreateSerializer):
    """Сериализатор данных регистрируемых пользователей."""

    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email', 'id', 'password'
        )
        read_only_fields = (
            'id',
        )


class RegisteredUserSerializer(UserSerializer):
    """Сериализатор данных зарегистрированных пользователей.

    Метод "get_is_subscribed" добавлен ввиду необходимостью генерировать
    статус: "подписан ли пользователь, инициирующий запрос,
    на другого пользователя".
    """

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'username', 'email', 'id', 'first_name', 'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        if self.context.get('request').user.is_anonymous:
            return False
        user = self.context.get('request').user
        return obj.authors.filter(
            user=user
        ).exists()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = (
            'id', 'name', 'measurement_unit'
        )


class IngredientAmountSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов рецепта с дополнительным полем amount.

    При регистрации нового рецепта пользователь должен
    указать id ингредиента и его количество.

    Необходимо обеспечить кастомный вывод полей в ответе,
    с полным описанием данных выбранного ингредиента,
    поэтому переопределен метод "to_representation".
    """
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    id = serializers.ReadOnlyField(
        source='ingredient.id'
    )
    amount = serializers.IntegerField(
        validators=[MinValueValidator(1)], required=True
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'name', 'measurement_unit', 'id', 'amount'
        )


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор добавленных в БД рецептов (сокращенный)."""

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'cooking_time'
        )


class RecipesSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов (полный).

    При регистрации нового рецепта необходимо дополнительно сохранить
    информацию для связанных полей по указанному в запросе
    списку id тегов, ингредиентов с уточнением количества.
    """

    tags = TagSerializer(
        many=True, read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = RegisteredUserSerializer(
        read_only=True
    )
    image = Base64ImageField()
    text = serializers.CharField(trim_whitespace=False,)
    cooking_time = serializers.IntegerField(
        validators=[MinValueValidator(1)]
    )
    ingredients = IngredientAmountSerializer(
        many=True, read_only=True, source='ingredients_recipes'
    )

    class Meta:
        model = Recipe
        fields = (
            'tags', 'is_favorited', 'is_in_shopping_cart', 'author', 'name',
            'image', 'text', 'cooking_time', 'id', 'ingredients'
        )

    def validate(self, data):
        tag_data = self.initial_data.get('tags')
        if not tag_data:
            raise serializers.ValidationError(
                "Необходимо указать теги"
            )
        elif len(tag_data) != len(set(tag_data)):
            raise serializers.ValidationError(
                "Теги не должны повторяться"
            )
        tags_set = [
            get_object_or_404(Tag, id=id) for id in tag_data
        ]
        data['tags'] = tags_set

        ingredient_data = self.initial_data['ingredients']
        ingredient_list = [
            item.get('id') for item in ingredient_data
        ]
        amount_list = [
            item.get('amount') for item in ingredient_data
        ]

        if not ingredient_data:
            raise serializers.ValidationError(
                "Необходимо указать ингредиенты"
            )
        if len(ingredient_list) != len(set(ingredient_list)):
            raise serializers.ValidationError(
                "Ингредиенты не должны повторяться"
            )

        ingredients = [
            get_object_or_404(
                Ingredient, id=id
            ) for id in ingredient_list
        ]
        amount_ingredients_set = dict(zip(ingredients, amount_list))
        data['ingredients'] = amount_ingredients_set

        return data

    def get_is_favorited(self, obj):
        if self.context.get('request').user.is_anonymous:
            return False
        user = self.context.get('request').user
        return obj.favorite_recipes.filter(owner=user).exists()

    def get_is_in_shopping_cart(self, obj):
        if self.context.get('request').user.is_anonymous:
            return False
        user = self.context.get('request').user
        return obj.shoppingcart_recipes.filter(owner=user).exists()

    def create(self, validated_data):
        user = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(
            author=user,
            **validated_data
        )

        recipe.tags.set(tags)

        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    ingredient=ingredient,
                    recipe=recipe,
                    amount=amount
                )
                for ingredient, amount in ingredients.items()
            ]
        )

        recipe.save()
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        instance.tags.clear()
        instance.tags.set(tags)

        instance.ingredients.clear()
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    ingredient=ingredient,
                    recipe=instance,
                    amount=amount
                )
                for ingredient, amount in ingredients.items()
            ]
        )

        return super().update(instance, validated_data)


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор подписки."""

    is_subscribed = serializers.SerializerMethodField()
    email = serializers.ReadOnlyField()
    id = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()
    first_name = serializers.ReadOnlyField()
    last_name = serializers.ReadOnlyField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField(default=0)

    class Meta:
        model = Follow
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return obj.authors.filter(user=user).exists()

    def get_recipes(self, obj):
        recipes_queryset = obj.recipes.all()
        recipes_limit = self.context.get('request').query_params.get(
            'recipes_limit')
        if recipes_limit:
            try:
                recipes_limit = _positive_int(recipes_limit)
                recipes_queryset = recipes_queryset[:recipes_limit]
            except (KeyError, ValueError):
                pass
        return ShortRecipeSerializer(
            recipes_queryset, many=True
        ).data
