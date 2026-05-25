from django.db import models
from django.contrib.auth.models import User
import re
from django.db.models import Max

# Create your models here.
class Recipes(models.Model):
    recipeID = models.AutoField(primary_key = True)
    title = models.CharField(max_length = 255)
    image = models.ImageField(upload_to = "recipeImages", blank = True, null = True)
    content = models.TextField()
    createdAt = models.DateTimeField(auto_now_add = True)
    updatedAt = models.DateTimeField(auto_now = True)
    servings = models.PositiveIntegerField()

    # Custom code here to parse input and convert to minutes/hours
    prepTime = models.PositiveIntegerField(
        help_text = "Preparation time in minutes",
        default = 0
    )

    cookTime = models.PositiveIntegerField(
        help_text = "Cooking time in minutes",
        default = 0
    )

    tags = models.ManyToManyField('Tag', related_name = 'recipe', blank = True)
    author = models.ForeignKey(User, on_delete = models.CASCADE)

    def __str__(self):
        return self.title
    
    def getDescription(self):
        words = self.content.split()

        if len(words) > 50:
            return ' '.join(words[:30])
        else:
            return self.content
    
class Tag(models.Model):
    name = models.CharField(max_length = 50, unique = True)

    def __str__(self):
        return self.name

class Ingredient(models.Model):
    name = models.CharField(max_length = 100, unique = True)
    fingerprint = models.CharField(max_length = 100, unique = True)

    def save(self, *args, **kwargs):
        # Automatically generate fingerprint before saving
        # Remove anything that isn't a letter or number
        self.fingerprint = self.generate_fingerprint(self.name)
        super().save(*args, **kwargs)

    @staticmethod
    def generate_fingerprint(text):
        # Normalizes input by standardizing the fingerprint
        # EX. Garlic-Powder -> garlicpowder
        if not text:
            return ""
        return re.sub(r'[^a-z0-9]', '', text.lower())

    @classmethod
    def find_name(cls, raw_name):
        # Lookup method to normalize user input and check fingerprint
        clean_name = raw_name.strip()
        fingerprint = cls.generate_fingerprint(clean_name)
        
        # Try to find an existing object, or create a new one
        instance = cls.objects.filter(fingerprint=fingerprint).first()

        if not instance:
            # Title here makes the display name look nice, while 
            # the fingerprint is normalized for querying/checking
            instance = cls.objects.create(name = clean_name.title())
        
        return instance

    def __str__(self):
        return self.name
    
class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipes, on_delete = models.CASCADE, related_name = 'RecipeIngredient')
    ingredient = models.ForeignKey(Ingredient, on_delete = models.CASCADE)
    quantity = models.DecimalField(max_digits=6, decimal_places=2)
    unit = models.CharField(max_length = 50)

class InstructionStep(models.Model):
    recipe = models.ForeignKey(Recipes, on_delete = models.CASCADE, related_name = 'steps')
    step_number = models.PositiveIntegerField(blank = True, null = True)
    text = models.TextField()

    class Meta:
        ordering = ['step_number']

    def save(self, *args, **kwargs):
        if not self.step_number:
            current_max = InstructionStep.objects.filter(recipe=self.recipe).aggregate(Max('step_number'))['step_number__max']
            self.step_number = (current_max or 0) + 1

        super().save(*args, **kwargs)

