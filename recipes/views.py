from django.shortcuts import render, redirect, get_object_or_404
from .models import Recipes, Tag, Ingredient, InstructionStep, RecipeIngredient
from .forms import RecipeForm,  RecipeIngredientForm, RecipeStepForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.db.models import IntegerField, Case, When, Value, Max
from django.db import transaction
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django.urls import reverse
from django.http import HttpResponse

# Create your views here.

@login_required(login_url = 'users:login')
def home(request):
    tags = Tag.objects.all()
    selectedTag = request.GET.get('tag')

    recipes = Recipes.objects.filter(author = request.user)

    if selectedTag:
        posts = posts.annotate(
            is_match = Max(Case(
                When(tags__name = selectedTag, then = Value(1)),
                default = Value(0),
                output_field = IntegerField()
            ))
        ).order_by('-is_match', '-created_at')
    else:
        recipes.order_by('-createdAt')

    recipes = recipes.distinct()

    context = {
        'recipes': recipes,
        'tags': tags,
        'selectedTag': selectedTag
    }

    return render(request, 'recipes/index.html', context)

@login_required(login_url = 'users:login')
def recipeDetails(request, pk):
    recipe = Recipes.objects.get(pk = pk)
    return render(request, 'recipes/details.html', {'recipe': recipe})

@login_required(login_url = 'users:login')
def editRecipe(request, pk):
    recipe = get_object_or_404(Recipes, pk = pk)

    if request.method == 'GET':
        form = RecipeForm(instance=recipe, initial = {
            'prep_hours': recipe.prepTime // 60,
            'prep_minutes': recipe.prepTime % 60,
            'cook_hours': recipe.cookTime // 60,
            'cook_mintues': recipe.cookTime % 60,
        })

        ing_forms = [RecipeIngredientForm(instance=i) for i in recipe.RecipeIngredient.all()]
        step_forms = [RecipeStepForm(instance=s) for s in recipe.steps.all()]

        if not ing_forms:
            ing_forms = [RecipeIngredientForm()]
        if not step_forms:
            step_forms = [RecipeStepForm()]

        context = {
            'form': form,
            'ing_forms': ing_forms,
            'step_forms': step_forms,
            'recipe': recipe
        }

        return render(request, 'partials/editRecipe.html', context)
    else:
        form = RecipeForm(request.POST, request.FILES, instance = recipe)

        if form.is_valid():
            with transaction.atomic():
                updated_recipe = form.save(commit = False)
                updated_recipe.author = request.user
                updated_recipe.save()
                form.save_m2m()

                recipe.steps.all().delete()
                recipe.RecipeIngredient.all().delete()

                for text in request.POST.getlist('text'):
                    if text.strip():
                        InstructionStep.objects.create(recipe = updated_recipe, text = text)

                quantities = request.POST.getlist('quantity')
                units      = request.POST.getlist('unit')
                ing_values = request.POST.getlist('ingredient')

                for qty, unit, ing_val in zip(quantities, units, ing_values):
                    if not ing_val or not qty:
                        continue
                    try:
                        ingredient = Ingredient.objects.get(pk=int(ing_val))
                    except (ValueError, Ingredient.DoesNotExist):
                        ingredient = Ingredient.find_name(ing_val)

                    RecipeIngredient.objects.create(
                        recipe=updated_recipe,
                        ingredient=ingredient,
                        quantity=qty,
                        unit=unit,
                    )
            response = HttpResponse()
            response['HX-Redirect'] = reverse('recipes:recipeDetails', kwargs={'pk': recipe.recipeID})
            return response
        
        context = {
            'form': form,
            'ing_forms': [RecipeIngredientForm()],
            'step_forms': [RecipeStepForm()],
            'recipe': recipe,
        }

        return render(request, 'partials/editRecipe.html', context)

    # if request.method == 'POST':
    #     print("POST CALLED")
    #     form = RecipeForm(request.POST, request.FILES, instance = recipe)
    #     ingredients = IngredientFormSet(request.POST, instance=recipe)
    #     steps = InstructionStepFormSet(request.POST, instance=recipe)

    #     if form.is_valid() and ingredients.is_valid() and steps.is_valid():
    #         form.save()
    #         ingredients.save()

    #         steps.save(commit = False)

    #         for deleted_step in steps.deleted_objects:
    #                 deleted_step.delete()
                
    #         num = 1
    #         for step in steps:
    #             if not step.cleaned_data or step in steps.deleted_forms:
    #                 continue
                
    #             step.instance.step_number = num
    #             step.instance.save()
    #             num+=1

    #         print("SAVED FORM")

    #         response = HttpResponse()
    #         response['HX-Redirect'] = reverse('recipes:home')
    #         return response
    #     else:
    #         print("--- VALIDATION FAILED ---")
    #         print("Main Form Errors:", form.errors.as_data())
    #         print("Main Form Non-Field:", form.non_field_errors())
            
    #         print("Ingredient Errors:", ingredients.errors)
    #         print("Ingredient Non-Form:", ingredients.non_form_errors())
            
    #         print("Step Errors:", steps.errors)
    #         print("Step Non-Form:", steps.non_form_errors())

    #         context = {
    #             'form': form,
    #             'recipe': recipe,
    #             'steps': steps,
    #             'ingredients': ingredients,
    #         }

    #         return render(request, 'partials/editRecipeTest.html', context)
        
    # else:
    #     print("GET CALLED")
    #     form = RecipeForm(instance = recipe)
    #     ingredients = IngredientFormSet(instance = recipe)
    #     steps = InstructionStepFormSet(instance = recipe)

    #     context = {
    #         'form': form,
    #         'recipe': recipe,
    #         'steps': steps,
    #         'ingredients': ingredients,
    #     }

        # return render(request, 'partials/editRecipeTest.html', context)
    return render(request, 'partials/editRecipeTest.html')

@login_required(login_url = 'users:login')
def deleteRecipe(request, pk):
    if request.method == 'POST':
        recipe = get_object_or_404(Recipes, pk=pk)

        recipe.delete()

        response = HttpResponse()
        response['HX-Redirect'] = reverse('recipes:home')
        return response
    
    print("GET DELETE NOT SUPPOSED TO HAPPEN")
    return render(request, 'recipes/home.html')

@login_required(login_url = 'users:login')
def about(request):
    return render(request, 'recipes/about.html')

@login_required(login_url = 'users:login')
def createStepRow(request):
    context = {
        'stepForm': RecipeStepForm()
    }

    return render(request, 'partials/stepForm.html', context)

@login_required(login_url = 'users:login')
def createIngredientRow(request):  
    context = {
        'ingForm': RecipeIngredientForm()
    }

    return render(request, 'partials/ingredientForm.html', context)

@login_required(login_url = 'users:login')
def create(request):
    # Retrieve initial empty form 
    if request.method == 'GET':
        form = RecipeForm()
        ingForm = RecipeIngredientForm()
        stepForm = RecipeStepForm()

        context = {
            'form': form,
            'ingForm': ingForm,
            'stepForm': stepForm
        }

        return render(request, 'recipes/create.html', context)
    else:
        # If its a post, then save everything
        form = RecipeForm(request.POST, request.FILES)

        if form.is_valid():
            with transaction.atomic():
                new_recipe = form.save(commit = False)
                new_recipe.author = request.user
                new_recipe.save()
                form.save_m2m()

                # save steps next    
                # Field name is 'text' in the form. so grab all the steps with that name and create new InstructionSteps tied to this recipe     
                for text in request.POST.getlist('text'):
                    if text.strip():
                        InstructionStep.objects.create(recipe = new_recipe, text=text)

                # Same thing here
                quantities = request.POST.getlist('quantity')
                units = request.POST.getlist('unit')
                ing_values = request.POST.getlist('ingredient')

                for qty, unit, ing_val in zip(quantities, units, ing_values):
                    # Stops us from iterating over potential empty rows
                    if not ing_val or not qty:
                        continue

                    # Check if the ingredient passed was an existing id, or a newly created string by the user
                    try:
                        ingredient = Ingredient.objects.get(pk=int(ing_val))
                    except (ValueError, Ingredient.DoesNotExist):
                        ingredient = Ingredient.find_name(ing_val)

                    # Ties the ingredient to our recipe
                    RecipeIngredient.objects.create(
                        recipe=new_recipe,
                        ingredient=ingredient,
                        quantity=qty,
                        unit=unit,
                    )

            # Because this form was posted via htmx, we have to also use htmx to redirect users
            response = HttpResponse()
            response['HX-Redirect'] = reverse('recipes:recipeDetails', kwargs={'pk': new_recipe.recipeID})
            return response
        
        context = {
            'form': form,
            'ingForm': RecipeIngredientForm(),
            'stepForm': RecipeStepForm(),
        }

        return render(request, 'recipes/create.html', context)

@login_required
def get_email_form(request):
    return render(request, 'partials/editEmail.html')

@login_required
def save_email(request):
    if request.method == 'POST':
        new_email = request.POST.get('email')

        if new_email:
            request.user.email = new_email
            request.user.save()

    return render(request, 'recipes/account.html')

@login_required
def get_password_form(request):
    form = SetPasswordForm(user = request.user)
    return render(request, 'partials/editPassword.html', {'form': form})

@login_required
def save_password(request):
    if request.method == 'POST':
        form = SetPasswordForm(user = request.user, data = request.POST)

        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return render(request, 'recipes/account.html')
        else:
            return render(request, 'partials/editPassword.html', {'form': form})

    return render(request, 'recipes/account.html')


def account(request):
    return render(request, 'recipes/account.html')

