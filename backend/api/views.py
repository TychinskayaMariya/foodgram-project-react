from api.pagination import CustomPagination
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from users.models import Follow, User

from .filters import IngredientFilter, RecipeFilter
from .permissions import IsOwnerOrAdmin
from .serializers import (CustomUserSerializer, FollowSerializer,
                          IngredientSerializer, RecipeCreateSerializer,
                          RecipeSerializer, RecipeShortSerializer,
                          TagSerializer)


class CustomUserViewSet(UserViewSet):
    """Вьюсет для работы с обьектами класса User и подписки на авторов."""

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPagination

    @action(
        detail=False,
        permission_classes=(IsAuthenticated, )
    )
    def subscriptions(self, request):
        """Возвращает список подписок пользователя."""

        queryset = User.objects.filter(subscribers__user=request.user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, **kwargs):
        """Подписывает или отписывает на другого пользователя."""

        user = request.user
        author = get_object_or_404(User, id=self.kwargs.get('id'))

        if request.method == 'POST':
            serializer = FollowSerializer(
                author, data=request.data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            subscription = get_object_or_404(
                Follow, user=user, author=author
            )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет работы с обьектами класса Tag."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для работы с обьектами класса Ingredient."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с обьектами класса Recipe."""

    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return RecipeCreateSerializer

    def get_permissions(self):
        if self.action in ('update', 'destroy'):
            return (IsOwnerOrAdmin(),)
        if self.action in ('create',):
            return (IsAuthenticated(),)
        return super().get_permissions()

    def add_to(self, model, user, pk):
        """Добавляет рецепт в указанную модель."""

        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response(
                {'Ошибка': 'Рецепт уже был добавлен'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeShortSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_from(self, model, user, pk):
        """Удаляет рецепт из указанной модели."""

        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'Ошибка': 'Рецепта не существует'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        detail=True,
        methods=['post', 'delete']
    )
    def favorite(self, request, pk):
        """Добавляет или удаляет рецепт из избранного у пользователя."""

        if request.method == 'POST':
            return self.add_to(Favorite, request.user, pk)
        return self.delete_from(Favorite, request.user, pk)

    @action(
        detail=True,
        methods=['post', 'delete']
    )
    def shopping_cart(self, request, pk):
        """Добавляет или удаляет рецепт из списка покупок пользователя."""

        if request.method == 'POST':
            return self.add_to(ShoppingCart, request.user, pk)
        return self.delete_from(ShoppingCart, request.user, pk)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Создает файл со списком покупок пользователя для скачивания."""

        user = request.user
        if not user.shopping_cart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        ingredients = (
            IngredientRecipe.objects
            .filter(recipe__in_shopping_cart__user=request.user)
            .values('ingredient')
            .annotate(total_amount=Sum('amount'))
            .values_list('ingredient__name',
                         'ingredient__measurements_unit',
                         'total_amount')
        )
        shopping_list = [('{} ({}) - {}'.format(*ingredient) + '\n')
                         for ingredient in ingredients]
        response = HttpResponse('Cписок покупок:\n' + '\n'.join(shopping_list),
                                content_type='text/plain')
        return response
