from django.shortcuts import render, redirect
from .forms import CustomUserForm
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from .forms import EditProfileForm

# Create your views here.
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username = username, password = password)

        if user is not None:
            login(request, user)
            return redirect('recipes:home')
        else:
            messages.info(request, 'Try again! Username or password is incorrect')

    context = {}
    return render(request, 'users/login.html', context)

def logoutPage(request):
    logout(request)
    return redirect('users:login')

def registerPage(request):
    if request.method != 'POST':
        form = CustomUserForm
    else:
        form = CustomUserForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('users:login')
    
    context = {'form': form}
    return render(request, 'users/register.html', context)

# @login_required
# def editProfile(request):
#     if request.method == 'POST':
#         form = EditProfileForm(request.POST, instance = request.user)

#         if form.is_valid():
#             form.save()
#             return redirect('users:login')
#         else:
#             form = EditProfileForm(instance = request.user)

#         return render(request, 'users/editProfile.html', {'form': form})
    
# @login_required
# def changePassword(request):
#     if request.method == 'POST':
#         form = PasswordChangeForm(request.user, request.POST)
#         if form.is_valid():
#             user = form.save()
#             update_session_auth_hash(request, user)
#             return redirect('users:login')
#     else:
#         form = PasswordChangeForm(request.user)

#     return render(request, 'users/changePassword.html', {'form': form})