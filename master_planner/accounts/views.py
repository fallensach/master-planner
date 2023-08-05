from django.shortcuts import render, redirect
from planning.forms import ProgramForm
from accounts.forms import CustomUserCreationForm
from planning.models import Program
from accounts.models import Account
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

    
def register(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            
            return redirect("login")
            
        else:
            form = CustomUserCreationForm(request.POST)

            context = {"form": form}
            return render(request, "registration/register.html", context)
    
    form = CustomUserCreationForm()
    context = {"form": form}

    return render(request, "registration/register.html", context)

def account_page(request):
    if not request.user.is_authenticated:
        return redirect("login")
    
    if request.method == "POST":
        form = ProgramForm(request.POST)
        if form.is_valid():
            program_name = request.POST.get("program")
            program = Program.objects.get(program_name=program_name)
            if program:
                account = request.user
                account.program = program
                account.save()
                return redirect("home")
            
            return redirect("setup")
            
                
    else:
        progs = list(Program.objects.all().values_list("program_name", flat=True))
        form = ProgramForm()

    return render(request, "overview.html", {"form": form, 
                                          "view": request.path,
                                          "setup_highlight": "bg-white/25 p-3 rounded-lg",
                                          "setup_p": "p-3",
                                          "setup_bg": "bg-white/25",
                                          "programs": progs
                                          })
