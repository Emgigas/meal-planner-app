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

    """