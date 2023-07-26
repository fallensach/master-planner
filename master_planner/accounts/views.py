from django.shortcuts import render, redirect
from .forms import RegisterForm
from planning.forms import ProgramForm
from planning.models import Program
from accounts.models import register_account, Account
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
    
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

def account_page(request):
    if not request.user.is_authenticated:
        return redirect("login")
    
    if request.method == "POST":
        form = ProgramForm(request.POST)
        if form.is_valid():
            program_name = request.POST.get("program")
            program = Program.objects.filter(program_name=program_name)
            if program:
                user = User.objects.get(username=request.user.username)
                account = Account.objects.get(user=user)
                program = program[0]
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