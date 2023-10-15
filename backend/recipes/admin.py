from django.contrib import admin

from .models import (Cart, Favorite, Follow, Ingredient, IngredientRecipe,
                     Recipe, Tag)

admin.site.empty_value_display = 'Значение не указано'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админ-панель управления тегами."""

    list_display = ('pk', 'name', 'slug')


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
    min_num = 1
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админ-панель управления рецептами."""

    list_display = ('pk', 'name', 'author', 'get_favorites', 'get_tags',)
    list_filter = ('author', 'name', 'tags')
    search_fields = ('name',)
    inlines = (IngredientRecipeInline,)

    def get_favorites(self, obj):
        return obj.favorites.count()

    get_favorites.short_description = (
        'Количество добавлений рецепта в избранное'
    )

    def get_tags(self, obj):
        return '\n'.join((tag.name for tag in obj.tags.all()))

    get_tags.short_description = 'Тег или список тегов'


@admin.register(IngredientRecipe)
class IngredientRecipeAdmin(admin.ModelAdmin):
    """Админ-панель управления соответствием ингредиентов и рецепта."""

    list_display = ('pk', 'ingredient', 'recipe', 'amount')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Админ-панель управления корзиной."""

    list_display = ('id', 'user', 'recipe')


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Админ-панель управления подписками."""

    list_display = ('pk', 'user', 'author')
    search_fields = ('user', 'author')
    list_filter = ('user', 'author')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Админ-панель управления избранными рецептами."""

    list_display = ('pk', 'user', 'recipe')
