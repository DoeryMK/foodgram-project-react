
from django.core.validators import MinValueValidator
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.pagination import _positive_int

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import Follow, User


class SignUpSerializer(UserCreateSerializer):
    """Сериализатор данных регистрируемых пользователей.

    SignUpSerializer является наследником класса UserCreateSerializer
    библиотеки Djoser с кастомными полями.

    Выполняет сериализацию данных при регистрации пользователей.
    """

    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email', 'id', 'password'
        )
        read_only_fields = (
            'id',
        )


class CustomUserSerializer(UserSerializer):
    """Сериализатор данных зарегистрированных пользователей.

    CustomUserSerializer является наследником класса UserSerializer
    библиотеки Djoser с кастомными полями.

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
    """Сериализатор тегов.

    Необходимо выполнять сериализацию добавленных в БД
    тегов/конкретного тега,
    отдаваемых/отдаваемого на чтение при get-запросе.
    """

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов.

    Необходимо выполнять сериализацию добавленных в БД
    ингредиентов/конкретного ингредиента,
    отдаваемых/отдаваемого на чтение при get-запросе."""

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

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source='ingredient', required=True
    )
    amount = serializers.IntegerField(
        validators=[MinValueValidator(1)], required=True
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id', 'amount'
        )

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep.pop('id')
        rep.pop('amount')
        rep['name'] = IngredientSerializer(
            instance.ingredient).data.get('name')
        rep['measurement_unit'] = IngredientSerializer(
            instance.ingredient).data.get('measurement_unit')
        rep['amount'] = instance.amount
        rep['id'] = instance.id
        return rep


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор добавленных в БД рецептов (сокращенный).

    Сериализация данных существующих рецептов
    для отображения сокращенной информации о рецепте
    при добавлении в избранное, в корзину, при подписке на автора рецепта.
    """

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'cooking_time'
        )


class RecipesSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов (полный).

    Сериализация данных для создания, обновления и просмотра рецепта

    При регистрации нового рецепта необходимо дополнительно сохранить
    информацию для связанных полей по указанному в запросе
    списку id тегов, ингредиентов с уточнением количества.

    Информация об авторе рецепта должна выводиться
    с указанием всех данных пользователя.

    Метод "get_is_favorited" добавлен ввиду необходимостью генерировать
    статус: "является ли рецепт в списке избранного у пользователя,
    инициирующий запрос"

    Метод "get_is_in_shopping_cart" добавлен ввиду необходимостью генерировать
    статус: "добавлен ли рецепт в корзину пользователя, инициирующего запрос"
    """

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = CustomUserSerializer(
        read_only=True
    )
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        validators=[MinValueValidator(1)]
    )
    ingredients = IngredientAmountSerializer(
        many=True, source='ingredients_recipes'
    )

    class Meta:
        model = Recipe
        fields = (
            'tags', 'is_favorited', 'is_in_shopping_cart', 'author', 'name',
            'image', 'text', 'cooking_time', 'id', 'ingredients'
        )

    def validate(self, data):
        tag_data = data['tags']
        if not tag_data:
            raise serializers.ValidationError(
                "Необходимо указать теги"
            )
        elif len(tag_data) != len(set(tag_data)):
            raise serializers.ValidationError(
                "Теги не должны повторяться"
            )

        ingredient_data = data['ingredients_recipes']
        ingredient_list = [item.get('ingredient') for item in
                           ingredient_data]
        if not ingredient_data:
            raise serializers.ValidationError(
                "Необходимо указать ингредиенты"
            )
        if len(ingredient_list) != len(set(ingredient_list)):
            raise serializers.ValidationError(
                "Ингредиенты не должны повторяться"
            )

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
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients_recipes')
        recipe = Recipe.objects.create(**validated_data)

        Recipe.tags.through.objects.bulk_create(
            [Recipe.tags.through(tag=tag, recipe=recipe) for tag in tags])

        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                ingredient=ingredient.get('ingredient'),
                recipe=recipe,
                amount=ingredient.get('amount'))

        return recipe

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients_recipes')

        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)

        instance.tags.clear()
        Recipe.tags.through.objects.bulk_create(
            [Recipe.tags.through(tag=tag, recipe=instance)
                for tag in tags_data])

        instance.ingredients.clear()
        for ingredient in ingredients_data:
            RecipeIngredient.objects.create(
                ingredient=ingredient.get('ingredient'),
                recipe=instance,
                amount=ingredient.get('amount'))

        instance.save()
        return instance

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['tags'] = TagSerializer(instance.tags, many=True).data
        return rep


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор подписки.

    Сериализация данных для создания, удаления подписки на автора,
    просмотра существующих подписок.
    Отображение связанных полей: данные автора, рецепты автора.

    Информация об авторе рецепта должна выводиться
    с указанием всех данных пользователя.

    Рецепты автора должны отображаться в сокращенном виде.

    Пользователь может ограничить отображением кол-ва
    рецептов автора параметром "recipes_limit".

    Метод "get_is_subscribed" добавлен ввиду необходимостью генерировать
    статус: "подписан ли пользователь, инициирующий запрос,
    на другого пользователя".

    Метод "get_recipes_count" добавлен ввиду необходимостью выводить
    общее количество зарегистрированных рецептов автора.
    """

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
