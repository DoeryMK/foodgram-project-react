from colorfield.fields import ColorField
from django.core.validators import MinValueValidator
from django.db import models

from users.models import User

LENGTH: int = 10


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название')
    colour = ColorField(
        max_length=7,
        default='#B3FF00',
        verbose_name='Цвет')
    slug = models.SlugField(
        max_length=200,
        unique=True,
        db_index=True,
        verbose_name='URL')

    class Meta:
        ordering = ['name']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.slug


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name='Название')
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единицы измерения')

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} - {self.measurement_unit}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор')
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата публикации')
    name = models.CharField(
        max_length=200,
        unique=True,
        db_index=True,
        verbose_name='Название')
    text = models.TextField(
        verbose_name='Описание')
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Картинка')
    cooking_time = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name='Время приготовления (в минутах)')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты')
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги')

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name}: {self.text[:LENGTH]}'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients_recipes',
        verbose_name='Рецепты')
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients_recipes',
        verbose_name='Ингредиенты')
    amount = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name='Количество')

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'
        constraints = [
            models.UniqueConstraint(fields=['recipe', 'ingredient'],
                                    name='unique_ingredient_in_recipe')]

    def __str__(self):
        return self.ingredient.name


class FavoriteBaseModel(models.Model):

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="%(class)s_owner",
        verbose_name='Владелец списка избранного')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="%(class)s_recipes",
        verbose_name='Рецепт')
    add_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата добавления')

    class Meta:
        abstract = True
        ordering = ['-add_date']
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(fields=['owner', 'recipe'],
                                    name='%(class)s_unique_favorite_recipes')]

    def __str__(self):
        return (f'Рецепт "{self.recipe.name}" понравившийся '
                f'пользователю {self.owner}')


class Favorite(FavoriteBaseModel):

    class Meta(FavoriteBaseModel.Meta):
        verbose_name = 'Список избранных рецептов'
        verbose_name_plural = 'Список избранных рецептов'


class ShoppingCart(FavoriteBaseModel):

    class Meta(FavoriteBaseModel.Meta):
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
