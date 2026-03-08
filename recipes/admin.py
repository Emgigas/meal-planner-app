from django.contrib import admin
from .models import Ingredient, Recipe, RecipeIngredient, RecipeSteps

class RecipeIngredientInline(admin.TabularInline):
    """
    Makes ingredients appear as rows inside the Recipe Edit page
    """
    model = RecipeIngredient
    extra = 3 # blank rows to fill in
    autocomplete_fields = ['ingredient']

class RecipeStepInline (admin.StackedInline):
    """
    Steps appear below recipe details, stacked vertically]
    Stacked Inline gives more room for instructions than TabularInline
    """
    model = RecipeSteps
    extra = 3

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['title', 'servings', 'prep_time_minutes',
                    'cook_time_minutes', 'source_type', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title', 'description', 'source_type']
    inlines = [RecipeIngredientInline, RecipeStepInline]

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']
    list_filter = ['category']
    search_fields = ['name']

@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ['recipe', 'ingredient', 'quantity', 'unit']
    search_fields = ['recipe__title', 'ingredient__name']