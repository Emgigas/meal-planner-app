from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.
class Ingredient(models.Model):
    """
    A generic ingredient that exists independently of any recipe.
    e.g. "plain flour", "eggs", "olive oil", etc.
    Stored separately so inventory can reference the same ingredient
    that recipes use
    """
    CATEGORY_CHOICES = [
        ('dairy', 'Dairy'),
        ('store_cupboard', 'Store Cupboard'),
        ('fresh_vegetables', 'Fresh Vegetables'),
        ('fresh_fruits', 'Fresh Fruits'),
        ('meat_fish', 'Meat & Fish'),
        ('frozen', 'Frozen'),
        ('sauces', 'Condiments & Sauces'),
        ('bakery', 'Bakery'),
        ('misc', 'Misc'),
    ]

    name = models.CharField(max_length=200)
    category = models.CharField(
        choices=CATEGORY_CHOICES,
        max_length=50,
        default='misc'
    )

    class Meta:
        ordering = ('name',) # alphabetical by default

    def __str__(self):
        return self.name

class Recipe(models.Model):
    """
    A complete recipe from a book, website, own creation.
    """
    SOURCE_TYPE_CHOICES = [
        ('book', 'Book'),
        ('url', 'URL'),
        ('self', 'Own Creation'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    servings = models.PositiveIntegerField(default=4)
    prep_time_minutes = models.PositiveIntegerField(null=True, blank=True)
    cook_time_minutes = models.PositiveIntegerField(null=True, blank=True)
    source_type = models.CharField(
        max_length=20,
        choices=SOURCE_TYPE_CHOICES,
        blank=True,
    )
    book_title = models.CharField(max_length=300, blank=True)
    page_number = models.PositiveIntegerField(null=True, blank=True)
    url = models.URLField(blank=True)
    source_notes = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    def clean(self):
        if self.source_type == 'book' and not self.book_title:
            raise ValidationError({
                'book_title': 'Book title is required for book sources.'
            })
        if self.source_type == 'url' and not self.url:
            raise ValidationError({
                'url': 'A URL is required for web sources.'
            })
        if self.source_type == 'other' and not self.source_notes:
            raise ValidationError({
                'source_notes': 'A note is required for other sources.'
            })

    @property
    def total_time_minutes(self):
        """Add prep and cook time together."""
        prep = self.prep_time_minutes or 0
        cook = self.cook_time_minutes or 0
        return prep + cook if (prep or cook) else None

class RecipeIngredient(models.Model):
    """
    The link between a Recipe and an Ingredient, with quantity info.
    Called a 'through table' or 'junction table' – it sits between
    Recipe and Ingredient and adds extra data to the relationship.

    e.g. "Chocolate Cake requires 200g of plain flour, sifted"
     recipe=ChocolateCake, ingredient=PlainFlour,
     quantity=200, unit='g', notes='sifted'
    """

    UNIT_CHOICES = [
        ('g', 'grams'),
        ('kg', 'kilograms'),
        ('ml', 'millilitres'),
        ('l', 'litres'),
        ('tsp', 'teaspoon'),
        ('tbsp', 'tablespoon'),
        ('cup', 'cup'),
        ('piece', 'piece(s)'),
        ('pinch', 'pinch'),
        ('handful', 'handful'),
        ('to_taste', 'to taste'),
    ]

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        related_name='recipe_ingredients'
    )
    quantity = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True
    )
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, blank=True)
    notes = models.CharField(
        max_length=200,
        blank=True,
        help_text='Notes about ingredient – e.g. finely chopped, room temperature, chopped/diced')

    class Meta:
        ordering = ['ingredient__name']

    def __str__(self):
        qty_str = f"{self.quantity} {self.unit} if self.quantity else ''"
        return f"{qty_str} {self.ingredient.name}".strip()

class RecipeSteps(models.Model):
    """
    A single step in a recipe's method, stored separately so we can
    number them, reorder them, and later add timers or images per step.
    """
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_steps'
    )
    step_number = models.PositiveIntegerField()
    instruction = models.TextField()

    class Meta:
        ordering = ['step_number']
        unique_together = ['recipe', 'step_number']

    def __str__(self):
        return f"Step {self.step_number} {self.instruction[:50]}..."