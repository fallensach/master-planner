from django.shortcuts import render, redirect
from .forms import ProgramForm, Profiles
from planning.models import register_program, get_courses, get_courses_term, Program, Profile, Schedule
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
    course_tags = {
                "Kurskod": "",
                "Kursnamn": "",
                "Hp": "",
                "Nivå": "",
                }
    if request.method == "POST":
        form = Profiles(profiles)
        profile_picked = True
        profile_code = request.POST.get("profiles")
        profile_name = profiles_dict[request.POST.get("profiles")]
        profile_courses = Profile.objects.get(profile_code=profile_code)
        for course in profile_courses.profile_courses.all():
            courses.append({
                "Kurskod": course.course_code,
                "Kursnamn": course.course_name,
                "Hp": course.hp,
                "Nivå": course.level,
                }
            )
    else:
        courses = [{}]
        form = Profiles(profiles)
    
    return render(request, "home.html", {"form": form, "profile_picked": profile_picked, "profile_name": profile_name, "courses": courses, "course_tags": course_tags})

def profile(request):
    user = User.objects.get(username=request.user.username)
    account = Account.objects.get(user=user)
    kurser = get_courses(account.program_code.program_code)
    name = account.program_code.program_name
    user_program = Program.objects.get(program_code=account.program_code.program_code)
    course_tags = {
                "Kurskod": "",
                "Kursnamn": "",
                "Hp": "",
                "Nivå": "",
                }
    profiles = []
    for profile in user_program.program_profiles.all():
        profiles.append((profile.profile_code, profile.profile_name))
    
    if request.method == "POST":
        if "pick_profile" in request.POST:
            profile_code = request.POST["profiles"]
            profile_name = Profile.objects.get(profile_code=profile_code).profile_name
            form = Profiles(profiles)
            return render(request, "home.html", {"term_courses": kurser, "program_name": name, "form": form, "profile_picked": True, "profile_code": profile_code, "profile_name": profile_name})
        
        if "t7" in request.POST:
            termin = request.POST.get("t7")
        
        elif "t8" in request.POST:
            termin = request.POST.get("t8")
        
        elif "t9" in request.POST:
            termin = request.POST.get("t9")

        profile_code = request.POST.get("profile_code")
        profile_courses = Profile.objects.get(profile_code=profile_code).profile_courses.all()
        profile_name = Profile.objects.get(profile_code=profile_code).profile_name
        term_courses = get_courses_term(account.program_code, termin, profile_courses=profile_courses)
        form = Profiles(profiles)
        return render(request, "home.html", {"term_courses": term_courses, "program_name": name, "termin": termin, "form": form, "profile_picked": True, "profile_code": profile_code, "profile_name": profile_name, "course_tags": course_tags})
    else:
        form = Profiles(profiles)
        return render(request, "home.html", {"term_courses": kurser, "program_name": name, "form": form})

def courses(request):
    if not request.user.is_authenticated:
        return redirect("login")
    
    user = User.objects.get(username=request.user.username)
    account = Account.objects.get(user=user)
    kurser = get_courses(account.program_code.program_code)
    name = account.program_code.program_name
    user_program = Program.objects.get(program_code=account.program_code.program_code)
    
    course_tags = {
                "Kurskod": "",
                "Kursnamn": "",
                "Hp": "",
                "Nivå": "",
                }
    profiles = []
    for profile in user_program.program_profiles.all():
        profiles.append((profile.profile_code, profile.profile_name))
    
    if request.method == "POST":
        if "t7" in request.POST:
            termin = request.POST.get("t7")
        
        elif "t8" in request.POST:
            termin = request.POST.get("t8")
        
        elif "t9" in request.POST:
            termin = request.POST.get("t9")
        
        term_courses = get_courses_term(account.program_code, termin)
        form = Profiles(profiles)
        return render(request, "home.html", {"term_courses": term_courses, "program_name": name, "termin": termin, "form": form, "course_tags": course_tags})
    else:
        form = Profiles(profiles)
        return render(request, "home.html", {"term_courses": kurser, "program_name": name, "form": form})

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