from django.core.validators import MinValueValidator
from django.db import models
from colorfield.fields import ColorField

from users.models import User


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
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} - {self.measurement_unit}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата публикации'
    )
    name = models.CharField(
        max_length=200,
        unique=True,
        db_index=True,
        verbose_name='Название')
    text = models.TextField(
        verbose_name='Описание')
    image = models.BinaryField()
    cooking_time = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name='Время приготовления (в минутах)')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE)
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиенты')
    amount = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name='Количество')

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'

    def __str__(self):
        return self.ingredient.name

