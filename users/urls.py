from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.loginPage, name = 'login'),
    path('register/', views.registerPage, name = 'register'),
    path('logout/', views.logoutPage, name = 'logout'),
    # path('editProfile/', views.editProfile, name = 'editProfile'),
    # path('changePassword/', views.changePassword, name = 'changePassword')
]