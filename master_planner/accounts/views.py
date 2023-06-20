from django.shortcuts import render, redirect
from django.http import HttpResponse
from scrappy.program_plan import ProgramPlan
from django.contrib.auth import authenticate
from .forms import RegisterForm, ProgramForm, ProfileCourses
from accounts.models import Account, register_account
from planning.models import register_program, Profile

def index(request):
    return HttpResponse()

def logged_in(request):
    if not request.user.is_authenticated:
        return redirect("/account/login")
    return HttpResponse("logged in")

def home(request):
    if request.method == "POST":
        form = ProgramForm(request.POST)
        form2 = ProfileCourses(request.POST)
        if form.is_valid():
            program_code = form.cleaned_data["program"]
            register_program(program_code)
        
        if form2.is_valid():
            profile_code = form2.cleaned_data["profile"]
            x = Profile.objects.get(profile_code=profile_code)
            print(x)
    
    else:
        form = ProgramForm()
        form2 = ProfileCourses(request.POST)

    return render(request, "home.html", {"form": form, "form2": form2})
    
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            email = form.cleaned_data["email"]
            register_account(username, email, password)
            return redirect("account/login")
    else:
        form = RegisterForm()
    
    return render(request, "registration/register.html", {"form": form})