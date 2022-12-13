from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from .models import Ingredient, Recipe, Tag, RecipeTag, RecipeIngredient


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    ordering = ('name',)
    empty_value_display = '-пусто-'
    list_per_page = 30


class RecipeTagInline(admin.TabularInline):
    model = RecipeTag
    raw_id_fields = ['tag']
    verbose_name = 'Тег'
    extra = 1

class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    raw_id_fields = ['ingredient']
    verbose_name = 'Ингредиент'
    extra = 1

# В inline добавить отображение не foreignKey, a названия, и сделать списком.
# На админ-странице рецепта отображается общее число добавлений этого рецепта в избранное.
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('author', 'name', 'cooking_time', 'pub_date')
    list_filter = ('author', 'name', 'tags')
    filter_vertical = ['tags', 'ingredients']
    inlines = [RecipeTagInline, RecipeIngredientInline]
    empty_value_display = '-пусто-'
    list_per_page = 30


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'colour', 'slug')
    ordering = ('name',)
    prepopulated_fields = {"slug": ("name",)}
    empty_value_display = '-пусто-'
    list_per_page = 30



admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)

