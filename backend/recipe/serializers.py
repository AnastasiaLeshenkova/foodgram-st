from rest_framework import serializers
from .models import (
    MeIngredient,
    MeCategory,
    MeRecipe,
    IngredientsRecipe,
    ShoppingList, Select)

from api.serializers import MeUserSerializer

class MeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингедиентов """

    class Meta:
        model = MeIngredient
        fields = '__all__'

class IngredientsRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов в рецепте"""
    name_ingredients = MeIngredientSerializer()

    class Meta:
        model = IngredientsRecipe
        fields = ['name_ingredients', 'quantity']

class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания ингредиентов в рецепте"""
    id = serializers.PrimaryKeyRelatedField(queryset=MeIngredient.objects.all())
    
    class Meta:
        model = IngredientsRecipe
        fields = ['id', 'quantity']

class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления рецептов"""
    ingredients = RecipeIngredientCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=MeCategory.objects.all(),
        many=True
    )
    
    class Meta:
        model = MeRecipe
        fields = [
            'name_recipe', 'illustration', 'discriptions', 'name_ingredients',
            'tags', 'time'
        ]
    
    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError("Добавьте хотя бы один ингредиент")
        ingredients = [item['id'] for item in value]
        if len(ingredients) != len(set(ingredients)):
            raise serializers.ValidationError("Ингредиенты не должны повторяться")
        return value
    
    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError("Добавьте хотя бы одину категорию")
        if len(value) != len(set(value)):
            raise serializers.ValidationError("Категории не должны повторяться")
        return value
    
    def create_ingredients(self, recipe, ingredients):
        IngredientsRecipe.objects.bulk_create([
            IngredientsRecipe(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            ) for ingredient in ingredients
        ])
    
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = MeRecipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe
    
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        
        instance.name = validated_data.get('name', instance.name)
        instance.illustration = validated_data.get('image', instance.illustration)
        instance.text = validated_data.get('text', instance.text)
        instance.time = validated_data.get('time', instance.time)
        
        instance.tags.clear()
        instance.tags.set(tags)
        
        instance.recipe_ingredients.all().delete()
        self.create_ingredients(instance, ingredients)
        
        instance.save()
        return instance
    
    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data
    
class MeCategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий """
    class Meta:
        model = MeCategory
        fields = '__all__'
    
class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецептов"""
    author = MeUserSerializer(read_only=True)
    tags = MeCategorySerializer(many=True, read_only=True)
    ingredients = IngredientsRecipeSerializer(
        many=True,
        source='recipe_ingredients',
        read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    
    class Meta:
        model = MeRecipe
        fields = [
            'id', 'author', 'name', 'image', 'text', 
            'ingredients', 'tags', 'cooking_time',
            'pub_date', 'is_favorited', 'is_in_shopping_cart'
        ]
    
    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Select.objects.filter(
                user=request.user,
                recipe=obj
            ).exists()
        return False
    
    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ShoppingList.objects.filter(
                user=request.user,
                recipe=obj
            ).exists()
        return False


class ShoppingListSerializer(serializers.ModelSerializer):
    """Сериализатор покупок """
    class Meta:
        model = ShoppingList
        fields = ['id', 'user', 'data']

    def to_representation(self, instance):
        return {
            'id': instance.recipe.id,
            'name_recipe': instance.recipe.name_recipe,
            'illustration': instance.recipe.illustration.url,
            'time': instance.recipe.time
        }
    
class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для избранного"""
    class Meta:
        model = Select
        fields = ['user', 'name_recipe']
    
    def to_representation(self, instance):
        return {
            'id': instance.recipe.id,
            'name_recipe': instance.recipe.name_recipe,
            'illustration': instance.recipe.illustration.url,
            'time': instance.recipe.time
        }

class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецептов"""
    author = MeUserSerializer(read_only=True)
    tags = MeCategorySerializer(many=True, read_only=True)
    ingredients = IngredientsRecipeSerializer(
        many=True,
        source='recipe_ingredients',
        read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    
    class Meta:
        model = MeRecipe
        fields = [
            'id', 'author', 'name_recipe', 'illustration', 'discriptions', 
            'name_ingredients', 'tags', 'time', 'date']
    
    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Select.objects.filter(
                user=request.user,
                recipe=obj
            ).exists()
        return False
    
    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ShoppingList.objects.filter(
                user=request.user,
                recipe=obj
            ).exists()
        return False


