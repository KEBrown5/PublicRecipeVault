from django.contrib import admin
from .models import Recipes, Tag, Ingredient, RecipeIngredient, InstructionStep
# Register your models here.

# admin.site.register(Recipes)
admin.site.register(Tag)
admin.site.register(Ingredient)

class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 0  # don't show blank rows

class RecipeStepInline(admin.TabularInline):
    model = InstructionStep
    extra = 0

@admin.register(Recipes)
class RecipesAdmin(admin.ModelAdmin):
    inlines = [RecipeIngredientInline, RecipeStepInline]