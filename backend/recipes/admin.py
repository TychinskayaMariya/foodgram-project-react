from django.contrib import admin
from django.contrib.admin import display

from .models import Cart, Favorite, Ingredient, IngredientRecipe, Recipe, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админ-панель управления тегами."""

    list_display = ('pk', 'name', 'color', 'slug')
    search_fields = ('name',)
    list_filter = ('slug',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админ-панель управления ингридиентами."""

    list_display = ('pk', 'name', 'measurement_unit')
    search_fields = ('name',)


class IngredientRecipeInline(admin.TabularInline):
    """
    Админ-панель управления ингредиентами в классе RecipeAdmin.
    """

    model = IngredientRecipe


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админ-панель управления рецептами."""

    list_display = ('pk', 'name', 'author', 'in_favorites',)
    list_filter = ('author', 'name', 'tags')
    search_fields = ('name',)
    inlines = (IngredientRecipeInline,)

    @display(description='Количество в избранных')
    def in_favorites(self, obj):
        return obj.favorites.count()


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Админ-панель управления корзиной."""

    list_display = ('id', 'user', 'recipe')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Админ-панель управления избранными рецептами."""

    list_display = ('pk', 'user', 'recipe')
