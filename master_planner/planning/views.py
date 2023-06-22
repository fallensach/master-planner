from django.shortcuts import render, redirect
from .forms import ProgramForm, ProfileCourses, Profiles
from planning.models import register_program, get_courses, Program, Profile
from accounts.models import Account, get_user
from django.contrib.auth.models import User

def home(request):
    if not request.user.is_authenticated:
        return redirect("login")
    
    account = Account.objects.get(user=get_user(request.user.username))

    if account.program_code is None:
        return redirect("setup")

    user_program = Program.objects.get(program_code=account.program_code.program_code)
    profiles = []
    for profile in user_program.program_profiles.all():
        profiles.append((profile.profile_code, profile.profile_name))
        
    profiles_dict = dict(profiles)
    profile_picked = False
    profile_name = None
    courses = []
    if request.method == "POST":
        form = Profiles(profiles)
        profile_picked = True
        profile_code = request.POST.get("profiles")
        profile_name = profiles_dict[request.POST.get("profiles")]
        profile_courses = Profile.objects.get(profile_code=profile_code)
        for course in profile_courses.profile_courses.all():
            courses.append({
                "course_code": course.course_code,
                "course_name": course.course_name,
                }
            )
    else:
        form = Profiles(profiles)
        
    print(courses)
    return render(request, "home.html", {"form": form, "profile_picked": profile_picked, "profile_name": profile_name, "courses": courses})

def courses(request):
    if not request.user.is_authenticated:
        return redirect("login")

    user = User.objects.get(username=request.user.username)
    account = Account.objects.get(user=user)
    kurser = get_courses(account.program_code.program_code)
    name = account.program_code.program_name
    return render(request, "courses.html", {"courses": kurser, "program_name": name})

def setup(request):
    if not request.user.is_authenticated:
        return redirect("login")
    
    if request.method == "POST":
        form = ProgramForm(request.POST)
        if form.is_valid():
            program_code = request.POST.get("program").upper()
            if register_program(program_code):
                user = User.objects.get(username=request.user.username)
                account = Account.objects.get(user=user)
                program = Program.objects.get(program_code=program_code)
                account.program_code = program
                account.save()
            return redirect("home")
                
    else:
        form = ProgramForm()

    return render(request, "setup.html", {"form": form})