from colorfield.fields import ColorField
from django.core.validators import MinValueValidator
from django.db import models
from users.models import User


class Tag(models.Model):
    """Модель тегов."""

    name = models.CharField(
        max_length=30,
        db_index=True,
        unique=True,
        verbose_name='Тег',
    )
    color = ColorField(
        unique=True,
        verbose_name='Цвет Hex',
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='slug',
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов."""

    name = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name='Ингредиент',
    )
    measurement_unit = models.CharField(
        max_length=20,
        verbose_name='Единицы измерения',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=["name", "measurement_unit"], name="unique_name_unit"
            )
        ]

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    """Модель рецептов."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    name = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name='Название блюда',
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Изображение блюда'
    )
    text = models.TextField(
        max_length=3000,
        verbose_name='Описание блюда',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        related_name='recipes',
        verbose_name='Список ингредиентов'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(
            1, 'Время приготовления блюда должно быть больше 0',
        )],
        verbose_name='Время приготовления'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    """Модель, связывающая классы Recipe и Ingredient."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(
            1, 'Количество должно быть больше 0',
        )],
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        ordering = ('id',)

    def __str__(self):
        return f'{self.ingredient.name} {self.amount}'


class ShoppingCart(models.Model):
    """Модель для формирования списка покупок в корзине."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_shopping_cart',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'], name='unique_shopping_cart_recipe'
            )
        ]

    def __str__(self):
        return (
            f'Рецепт {self.recipe.name} в списке покупок'
            f'у {self.user.username}'
        )


class Favorite(models.Model):
    """Модель избранных рецептов"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favorite_recipe'
            )
        ]

    def __str__(self):
        return f'Рецепт {self.recipe.name} в избранном у {self.user.username}'
