from django.shortcuts import render, redirect
from account.forms import CreateUserForm
from banco_america.forms import CreateClientForm, CreateAddressForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
# Create your views here.

def home(request):
    context = {}
    return render(request, 'registration/home.html', context)


def registrate(request):
    if request.method == "POST":   
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'You have successfuly been registrated.')
            return redirect('account:login')

    else:
        form = CreateUserForm()
    context = {"form":form}
    return render(request, 'registration/registrate.html',context)


def login_user(request):
    context = {}
    return render(request, 'registration/login.html', context)

def logout_user(request):
    logout(request)
    context = {}
    return render(request, 'registration/logout_user.html', context)