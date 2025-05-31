from django.db import models
from django.core.validators import MinValueValidator
from api.models import MeUser
from django.db.models import UniqueConstraint

class MeCategory(models.Model):
    """ Модель категории """

    name_category = models.CharField(max_length=70, verbose_name="Название категории", unique=True)
    slug = models.SlugField(max_length=70, verbose_name="Слаг категории", unique=True)
    color = models.CharField(null=True, max_length=7, unique=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name_category

class MeIngredient(models.Model):
    """Модель ингредиента"""

    name = models.CharField(max_length=70, verbose_name='Название ингредиента')
    unit_of_measure = models.CharField(max_length=70, verbose_name='Единица объема')
    
    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингридиенты"
    
    def __str__(self):
        return f'{self.name}, {self.unit_of_measure}'
    
class MeRecipe(models.Model):
    """Модель рецепта"""

    name_recipe = models.CharField(max_length=150, verbose_name='Название рецепта')

    author = models.ForeignKey(
        MeUser,
        on_delete=models.CASCADE,
        verbose_name="Автор рецепта")
    
    name_ingredients = models.ManyToManyField(
        MeIngredient,
        verbose_name='Ингредиенты для рецепта',
        through='IngredientsRecipe'     
    )

    category = models.ManyToManyField(
        MeCategory,
        verbose_name='Категория рецепта',
        related_name='me_recipes'    
    )

    discriptions = models.TextField(verbose_name="Описание рецепта", null=False, blank=False)

    illustration = models.ImageField(verbose_name="Фото рецепта")

    data = models.DateTimeField(verbose_name="Дата добавления рецепта")

    time = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Время приготовления рецепта(значение не меньше 1 минуты)'
    )

    tags = models.ManyToManyField(
        MeCategory, 
        related_name='me_recipes_with_tags',
        verbose_name='Категория')

    class Meta:
        verbose_name='Рецепт'
        verbose_name_plural='Рецепты'

    def __str__(self):
        return self.name_recipe
    
class IngredientsRecipe (models.Model):
    """ Модель для ингридиент в рецепт"""

    name_recipe = models.ForeignKey(
        MeRecipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name='recipe_ingredients' 
    )

    name_ingredients = models.ForeignKey(
        MeIngredient,
        on_delete=models.CASCADE,
        verbose_name="Ингридиент",
        related_name='ingredient_recipes',
    ) 

    quantity = models.PositiveIntegerField(
        verbose_name="Количество ингредиентов, не менее одного",
        validators=[MinValueValidator(1)]
    )
    def __str__(self):
        return f'{self.name_ingredients} в {self.name_recipe}'

    class Meta:
        verbose_name='Ингредиент для рецепта'
        verbose_name_plural='Ингредиенты для рецепта'

class Select(models.Model):
    """Избранные рецепты"""

    user = models.ForeignKey(
        MeUser,
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )

    name_recipe = models.ForeignKey(
        MeRecipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт"
    )

    data = models.DateTimeField(
        verbose_name="Дата добавления рецепта в Избранное"
    )

    class Meta:
        verbose_name='Избранное'
        verbose_name_plural='Избранное',

    def __str__(self):
        return f'Данный рецепт {self.name_recipe} в избранном у пользователя - {self.user}'
    
class ShoppingList(models.Model):
    """Список для покупок"""

    user = models.ForeignKey(
        MeUser,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )

    recipe = models.ForeignKey(
        MeRecipe,
        on_delete=models.CASCADE,
        related_name='in_shopping_cart',
        verbose_name='Рецепт'
    )
    
    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            )
        ]
    
    def __str__(self):
        return f'{self.recipe} в списке покупок у {self.user}'

    data = models.DateTimeField(
        verbose_name="Дата добавления в список"
    )