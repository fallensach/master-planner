from django.shortcuts import render, redirect
from .forms import ProgramForm, Profiles
from planning.models import register_program, get_courses, get_courses_term, Program, Profile, Schedule
from accounts.models import Account, get_user
from django.contrib.auth.models import User

def profile_pick(request):
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
                "hp": course.hp,
                "level": course.level,
                }
            )
    else:
        form = Profiles(profiles)
        
    return render(request, "home.html", {"form": form, "profile_picked": profile_picked, "profile_name": profile_name, "courses": courses})

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
                "hp": course.hp,
                "level": course.level,
                }
            )
    else:
        form = Profiles(profiles)
        
    return render(request, "home.html", {"form": form, "profile_picked": profile_picked, "profile_name": profile_name, "courses": courses})

def courses(request):
    if not request.user.is_authenticated:
        return redirect("login")
    
    user = User.objects.get(username=request.user.username)
    account = Account.objects.get(user=user)
    kurser = get_courses(account.program_code.program_code)
    name = account.program_code.program_name
    
    profile_courses = Profile.objects.get(profile_code="DAIM").profile_courses.all()
    distinct_course_codes = Schedule.objects.filter(course_code__in=profile_courses).values('course_code').distinct()
    matching_schedules = Schedule.objects.filter(course_code__in=distinct_course_codes)
    
    for i in matching_schedules:
        print(i.course_code.course_code)

    if request.method == "POST":
        if "t7" in request.POST:
            termin = request.POST.get("t7")
        
        elif "t8" in request.POST:
            termin = request.POST.get("t8")
        
        elif "t9" in request.POST:
            termin = request.POST.get("t9")
        
        term_courses = get_courses_term(account.program_code, termin)
        return render(request, "courses.html", {"courses": term_courses, "program_name": name, "termin": termin})
    else:
        
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