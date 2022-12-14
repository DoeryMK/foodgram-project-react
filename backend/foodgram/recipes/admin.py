from django.contrib import admin


from .models import Ingredient, Recipe, Tag, RecipeIngredient


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)
    ordering = ('name',)
    empty_value_display = '-пусто-'
    list_per_page = 30


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    fields = ('ingredient', 'amount')
    autocomplete_fields = ('ingredient',)
    extra = 1
    verbose_name = 'Ингредиент'


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'colour', 'slug')
    search_fields = ['name']
    ordering = ('name',)
    prepopulated_fields = {"slug": ("name",)}
    empty_value_display = '-пусто-'
    list_per_page = 30


# На админ-странице рецепта отображается общее число добавлений этого рецепта в избранное.
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('author', 'name', 'cooking_time', 'pub_date')
    list_select_related = ('author',)
    list_filter = ('name', 'author', 'tags')
    search_fields = ('name', 'author', 'tags')
    filter_horizontal = ('tags',)
    inlines = (RecipeIngredientInline,)
    autocomplete_fields = ('tags', 'author',)
    empty_value_display = '-пусто-'
    list_per_page = 30


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)

