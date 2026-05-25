from django.urls import path, include
from . import views

app_name = 'recipes'

urlpatterns = [
    path('home/', views.home, name = 'home'),
    path('create/', views.create, name = 'create'),
    path('about/', views.about, name = 'about'),
    path('account/', views.account, name = 'account'),
    # path('<int:pk>/', views.recipeDetails, name = 'recipeDetails'),
    path('recipes/<int:pk>/', views.recipeDetails, name = 'recipeDetails'),
    path('recipes/<int:pk>/edit', views.editRecipe, name = 'editRecipe'),
    path('createIngredientRow/', views.createIngredientRow, name = 'createIngredientRow'),
    path('createStepRow/', views.createStepRow, name = 'createStepRow'),
    path('account/email/edit/', views.get_email_form, name = 'get_email_form'),
    path('account/email/save/', views.save_email, name = 'save_email'),
    path('account/password/edit/', views.get_password_form, name = 'get_password_form'),
    path('account/password/save/', views.save_password, name = 'save_password'),
    path('recipes/<int:pk>/delete', views.deleteRecipe, name = 'deleteRecipe'),
]