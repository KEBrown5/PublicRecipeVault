from django import forms
from .models import Recipes, RecipeIngredient, InstructionStep, Ingredient
from django.forms import inlineformset_factory

class RecipeForm(forms.ModelForm):
    prep_hours = forms.IntegerField(min_value = 0, required = False, initial = 0)
    prep_minutes = forms.IntegerField(min_value = 0, max_value = 59, required = False, initial = 0)

    cook_hours = forms.IntegerField(min_value = 0, required = False, initial = 0)
    cook_minutes = forms.IntegerField(min_value = 0, max_value = 59, required = False, initial = 0)

    class Meta:
        model = Recipes
        fields = ['title', 'content', 'image', 'tags', 'servings']
        widgets = {
            'title': forms.TextInput(attrs = {'placeholder': 'Add title here'}),
            'content': forms.Textarea(attrs = {'rows': '6', 'placeholder': 'Add description here'}),
            'servings': forms.NumberInput(attrs = {'placeholder': 'Add servings here', 'min': '0'}),
            'tags': forms.SelectMultiple(attrs = {'class': 'tagSelect'}),
            # 'prepTime': forms.NumberInput(attrs = {'placeholder': 'Minutes', 'min': '0'}),
            # 'cookTime': forms.NumberInput(attrs = {'placeholder': 'Minutes', 'min': '0'})
        }

    def clean(self):
            cleaned_data = super().clean()

            # Grab the UI inputs, default to 0 if blank
            p_hrs = cleaned_data.get('prep_hours') or 0
            p_mins = cleaned_data.get('prep_minutes') or 0
            c_hrs = cleaned_data.get('cook_hours') or 0
            c_mins = cleaned_data.get('cook_minutes') or 0

            # Convert to total mins
            total_prep_minutes = (p_hrs * 60) + p_mins
            total_cook_minutes = (c_hrs * 60) + c_mins

            # Inject new values into cleaned_data
            cleaned_data['prep_time'] = total_prep_minutes
            cleaned_data['cook_time'] = total_cook_minutes

            return cleaned_data
        
    def save(self, commit = True):
        # Intercept save process to assign our custom values to the model instance
        instance = super().save(commit = False)
        instance.prepTime = self.cleaned_data['prep_time']
        instance.cookTime = self.cleaned_data['cook_time']

        if commit:
            instance.save()

        return instance

class RecipeIngredientForm(forms.ModelForm):
    class Meta:
        model = RecipeIngredient
        fields = ['ingredient', 'quantity', 'unit']
        widgets = {
            'quantity': forms.NumberInput(attrs = {'class': 'form-control', 'placeholder': 'Quantity', 'min': '0'}),
            'unit': forms.TextInput(attrs = {'class': 'form-control', 'placeholder': 'Unit'}),
            'ingredient': forms.Select(attrs = {'class': 'select2-ingredient', 'id': ''})
        }

class RecipeStepForm(forms.ModelForm):
    class Meta:
        model = InstructionStep
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs = {'rows': '2', 'placeholder': 'Input step here', 'name': 'step_text', 'class': 'stepTextInput'})
        }