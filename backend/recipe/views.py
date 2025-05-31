from rest_framework import viewsets, permissions, status
from .models import MeIngredient, MeCategory, MeRecipe, Select, ShoppingList
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from .models import (
    MeRecipe, MeCategory, MeIngredient, 
    Select, ShoppingList
)

from .serializers import (
    MeIngredientSerializer,
    MeCategorySerializer,
    ShoppingListSerializer,
    RecipeCreateUpdateSerializer,
    RecipeReadSerializer,
    FavoriteSerializer
)
#from api.serializers import MeRecipeSerializer

from django_filters.rest_framework import DjangoFilterBackend
from .filters import RecipeFilter

from .utils import generate_pdf_shopping_list, generate_txt_shopping_list

class MeIngredientViewSet(viewsets.ModelViewSet):
    """Представление для ингредиентов"""
    queryset = MeIngredient.objects.all()
    serializer_class = MeIngredientSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__istartswith=name)
        return queryset

class MeCategoryViewSet(viewsets.ModelViewSet):
    """Представление для категорий"""
    queryset = MeCategory.objects.all()
    serializer_class = MeCategorySerializer

class MeRecipeViewSet(viewsets.ModelViewSet):
    """Представление для рецептов"""
    queryset = MeRecipe.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeCreateUpdateSerializer
        return RecipeReadSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset().select_related('author')
        queryset = queryset.prefetch_related('tags', 'recipe_ingredients__ingredient')
        
        # Фильтрация по избранному
        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited and self.request.user.is_authenticated:
            queryset = queryset.filter(in_favorites__user=self.request.user)
        
        # Фильтрация по списку покупок
        is_in_shopping_cart = self.request.query_params.get('is_in_shopping_cart')
        if is_in_shopping_cart and self.request.user.is_authenticated:
            queryset = queryset.filter(in_shopping_cart__user=self.request.user)
        
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        """Добавление/удаление рецепта в избранное"""
        recipe = get_object_or_404(MeRecipe, id=pk)
        
        if request.method == 'POST':
            data = {'user': request.user.id, 'recipe': recipe.id}
            serializer = FavoriteSerializer(
                data=data,
                context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data, 
                    status=status.HTTP_201_CREATED
                )
            return Response(
                serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        elif request.method == 'DELETE':
            favorite = get_object_or_404(
                Select,
                user=request.user,
                recipe=recipe
            )
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk=None):
        """Добавление/удаление рецепта в список покупок"""
        recipe = get_object_or_404(MeRecipe, id=pk)
        
        if request.method == 'POST':
            data = {'user': request.user.id, 'recipe': recipe.id}
            serializer = ShoppingListSerializer(
                data=data, 
                context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data, 
                    status=status.HTTP_201_CREATED
                )
            return Response(
                serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        elif request.method == 'DELETE':
            cart_item = get_object_or_404(
                ShoppingList,
                user=request.user,
                recipe=recipe
            )
            cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        """Скачивание списка покупок"""
        format = request.query_params.get('format', 'txt')
        
        if format == 'pdf':
            buffer = generate_pdf_shopping_list(request.user)
            response = HttpResponse(
                buffer, 
                content_type='application/pdf'
            )
            response['Content-Disposition'] = 'attachment; filename="shopping_list.pdf"'
        else:
            content = generate_txt_shopping_list(request.user)
            response = HttpResponse(
                content, 
                content_type='text/plain'
            )
            response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
        
        return response
