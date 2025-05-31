from django.http import HttpResponse
from reportlab.pdfgen import canvas
from io import BytesIO
from .models import IngredientsRecipe, ShoppingList
from collections import defaultdict

def generate_shopping_list(user):
    """Генерация списка покупок"""
    shopping_cart = ShoppingList.objects.filter(user=user).select_related('recipe')
    ingredients = defaultdict(lambda: {'amount': 0, 'unit': ''})
    
    for item in shopping_cart:
        for ri in item.recipe.recipe_ingredients.all():
            key = ri.ingredient.name
            ingredients[key]['amount'] += ri.amount
            ingredients[key]['unit'] = ri.ingredient.measurement_unit
    
    return ingredients


def generate_pdf_shopping_list(user):
    """Генерация PDF со списком покупок"""
    ingredients = generate_shopping_list(user)
    
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    
    # Список покупок
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 800, "Список покупок")
    p.setFont("Helvetica", 12)
    
    # Список ингредиентов
    y = 750
    for name, data in ingredients.items():
        p.drawString(100, y, f"- {name} ({data['unit']}) — {data['amount']}")
        y -= 20
        if y < 50:
            p.showPage()
            y = 750
    
    p.save()
    buffer.seek(0)
    return buffer


def generate_txt_shopping_list(user):
    """Генерация TXT со списком покупок"""
    ingredients = generate_shopping_list(user)
    
    content = "Список покупок:\n\n"
    for name, data in ingredients.items():
        content += f"- {name} ({data['unit']}) — {data['amount']}\n"
    
    return content
