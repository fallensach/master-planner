from django.shortcuts import render, redirect
from .forms import RegisterForm
from accounts.models import register_account
from django.contrib.auth import authenticate, login
    
def register(request):
    if request.user.is_authenticated:
        return redirect("home")

    success = True
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = request.POST.get("username")
            password = request.POST.get("password")
            email = request.POST.get("email")
            success = register_account(username, email, password)
            
            if success:
                user = authenticate(request, username=username, password=password)
                login(request, user)
                return redirect("home")
            else:
                form = RegisterForm()
                return render(request, "registration/register.html", {"form": form, "success": success})
    else:
        form = RegisterForm()
    
    return render(request, "registration/register.html", {"form": form, "success": success})