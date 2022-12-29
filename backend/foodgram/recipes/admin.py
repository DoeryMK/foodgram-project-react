from django.contrib import admin
from django.db.models import Count

from .models import Ingredient, Recipe, RecipeIngredient, Tag, Favorite, \
    ShoppingCart


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)
    ordering = ('id',)
    empty_value_display = '-пусто-'
    list_per_page = 30


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    fields = ('ingredient', 'amount')
    autocomplete_fields = ('ingredient',)
    extra = 1
    verbose_name = 'Ингредиент'


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'colour', 'slug')
    search_fields = ('name',)
    ordering = ('name',)
    prepopulated_fields = {"slug": ("name",)}
    empty_value_display = '-пусто-'
    list_per_page = 30


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'name', 'cooking_time', 'pub_date',
                    'recipe_likes_counter')
    list_select_related = ('author',)
    list_filter = ('name', 'author', 'tags')
    search_fields = ('name', 'author', 'tags')
    filter_horizontal = ('tags',)
    inlines = (RecipeIngredientInline,)
    autocomplete_fields = ('tags', 'author',)
    empty_value_display = '-пусто-'
    list_per_page = 30

    def recipe_likes_counter(self, obj):
        return obj.recipe_likes_counter

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            recipe_likes_counter=Count('favorite_recipes', distinct=True))
        return queryset

    recipe_likes_counter.short_description = "Число добавлений в избранное"


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('owner', 'recipe')
    list_filter = ('recipe',)
    search_fields = ('owner',)


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('owner', 'recipe')
    list_filter = ('recipe',)
    search_fields = ('owner',)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
