from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Recipes, Tag, Ingredient
from .forms import RecipeForm,  IngredientFormSet, InstructionStepFormSet
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.db.models import IntegerField, Case, When, Value, Max
from django.db import transaction
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm

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
def editRecipe(request, key):
    recipe = get_object_or_404(Recipes, pk = key)

    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES, instance = recipe)

        if form.is_valid():
            form.save()
            return redirect('recipes:home')
    else:
        form = RecipeForm(instance = recipe)

    return render(request, 'recipes/edit.html', {'form': form})

# @login_required(login_url = 'users:login')
# def deleteRecipe

def about(request):
    return render(request, 'recipes/about.html')

@login_required(login_url = 'users:login')
def createStepRow(request):
    total = int(request.POST.get('steps-TOTAL_FORMS'))
    step_number = request.POST.get('steps-__prefix__-step_number')
    text = request.POST.get('steps-__prefix__-text')

    form = InstructionStepFormSet().empty_form

    form.initial = {
        'step_number': step_number,
        'text': text,
    }

    form.prefix = f'steps-{total}'
    form.data = {
        f'{form.prefix}-step_number': step_number,
        f'{form.prefix}-text': text,
    }

    context = {
        'form': form,
        'total': total + 1,
    }

    return render(request, 'partials/step.html', context)

@login_required(login_url = 'users:login')
def createIngredientRow(request):  
    ingredientID = request.POST.get('RecipeIngredient-__prefix__-ingredient')
    quantity = request.POST.get('RecipeIngredient-__prefix__-quantity')
    unit = request.POST.get('RecipeIngredient-__prefix__-unit')
    total = int(request.POST.get('RecipeIngredient-TOTAL_FORMS', 0))

    # This try/except block is necessary as the drop down in the form uses the ID values of ingredients
    # to display, as well as pass them. This means that if users use an existing ingredient from the menu,
    # it will pass an ID. If they create a new ingredient on the spot, it will instead pass the name they created.
    # If an ID already exists, continue through
    try:
        ingredientID = int(ingredientID)
    # Otherwise if our input is a new string (I.E the key doesn't exist), create a new ingredient
    except (ValueError, TypeError):
        if ingredientID and ingredientID.strip():
            # Call cleaning methods
            ingredient = Ingredient.find_name(ingredientID)
            print(f"CREATED NEW INGREDIENT: {ingredient}")
            ingredientID = ingredient.id
        else:
            print("ERROR")

    form = IngredientFormSet().empty_form

    form.initial = {
        'ingredient': ingredientID,
        'quantity': quantity,
        'unit': unit,
    }

    form.prefix = f'RecipeIngredient-{total}'

    form.data = {
        f'{form.prefix}-ingredient': ingredientID,
        f'{form.prefix}-quantity': quantity,
        f'{form.prefix}-unit': unit,
    }

    context = {'form': form,
               'total': total + 1,
               'name': Ingredient.objects.filter(id=ingredientID).first()}
    
    return render(request, 'partials/form.html', context)

@login_required(login_url = 'users:login')
def create(request):
    if request.method == 'POST': 
        print(request.POST)      
        form = RecipeForm(request.POST, request.FILES)
        formset = IngredientFormSet(request.POST)
        stepset = InstructionStepFormSet(request.POST)

        if form.is_valid() and formset.is_valid() and stepset.is_valid():
            with transaction.atomic():
                recipe = form.save(commit = False)
                recipe.author = request.user
                recipe.save()
                form.save_m2m()

                formset.instance = recipe
                formset.save()

                stepset.instance = recipe

                steps = stepset.save(commit = False)
                for num, step in enumerate(steps, start = 1):
                    step.step_number = num
                    step.save()

                # stepset.save()

            return redirect('recipes:home')
        else:
            print("Form errors:", form.errors)
            print("Formset errors:", formset.errors)
            print("Stepset errors: ", stepset.errors)
            print("Non-formset errors:", formset.non_form_errors())
    else:
        form = RecipeForm()
        formset = IngredientFormSet()
        stepset = InstructionStepFormSet()

    context = {'form': form,
                'formset': formset,
                'stepset': stepset}
    
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

