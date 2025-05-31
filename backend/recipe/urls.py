from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MeCategoryViewSet,
    MeIngredientViewSet,
    MeRecipeViewSet
)

router = DefaultRouter()
router.register(r'tags', MeCategoryViewSet, basename='tags')
router.register(r'ingredients', MeIngredientViewSet, basename='ingredients')
router.register(r'recipes', MeRecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
]