from django.shortcuts import render, redirect
from .forms import ProgramForm, Profiles
from planning.models import get_profile_courses, get_program_courses, get_courses_term, Program, Profile, Schedule
from accounts.models import Account, get_user
from django.contrib.auth.models import User


COURSE_TAGS = {
                "Kurskod": "",
                "Kursnamn": "",
                "Hp": "",
                "Nivå": "",
                "Vof": "",
                "": "",
                }

def test(request):
    return render(request, "test.html")

def home(request):
    
    if not request.user.is_authenticated:
        return redirect("login")
    
    account = Account.objects.get(user=get_user(request.user.username))

    if account.program is None:
        return redirect("setup")

    user_program = account.program
    profiles = [(profile.profile_code, profile.profile_name) for profile in user_program.profiles.all()]
    profiles_dict = dict(profiles) 
    profile_picked = False
    profile_name = None
    courses = []
    
    if request.method == "POST":
        form = Profiles(profiles)
        profile_picked = True
        profile_code = request.POST.get("profiles")
        profile_name = profiles_dict[request.POST.get("profiles")]
        profile = Profile.objects.get(profile_code=profile_code)

        scheduler = Scheduler.objects.filter(profile=profile.profile_code)
        for row in scheduler:
            courses.append(row.course.to_dict)
            
    else:
        courses = [{}]
        form = Profiles(profiles)
    
    return render(request, "home.html", {"form": form, 
                                         "profile_picked": profile_picked, 
                                         "profile_name": profile_name, 
                                         "courses": courses, 
                                         "course_tags": COURSE_TAGS})

def profile(request):
    user = User.objects.get(username=request.user.username)
    account = Account.objects.get(user=user)
    courses = get_program_courses(account.program)
    user_program = account.program
    course_tags = {
                "Kurskod": "",
                "Kursnamn": "",
                "Hp": "",
                "Nivå": "",
                }
    profiles = map(lambda profile : (profile.profile_code, profile.profile_name), 
                   user_program.profiles.all()
                   )
    
    if request.method == "POST":
        if "pick_profile" in request.POST: #TODO shuldnt this be a GET?
            profile_code = request.POST["profiles"] #TODO maybe rename to profile_code
            profile_name = Profile.objects.get(profile_code=profile_code).profile_name
            form = Profiles(profiles)
            return render(request, "home.html", {"term_courses": courses, "program_name": user_program.program_name, "form": form, "profile_picked": True, "profile_code": profile_code, "profile_name": profile_name})
>>>>>>> 8775cbb (New database design is now implemented, works with views,)
        
        if "t7" in request.POST:
            semester = request.POST.get("t7")
        
        elif "t8" in request.POST:
            semester = request.POST.get("t8")
        
        elif "t9" in request.POST:
            semester = request.POST.get("t9")

        profile_code = request.POST.get("profile_code")
        # profile_courses = Profile.objects.get(profile_code=profile_code).profile_courses.all()
        profile = Profile.objects.get(profile_code=profile_code)
        profile_name = profile.profile_name
        semester_courses = get_courses_term(program=account.program, semester=semester, profile=profile)
        form = Profiles(profiles)
        return render(request, "home.html", {"term_courses": term_courses, 
                                             "program_name": name, 
                                             "termin": termin, 
                                             "form": form, 
                                             "profile_picked": True, 
                                             "profile_code": profile_code, 
                                             "profile_name": profile_name, 
                                             "course_tags": COURSE_TAGS}
                     )
    else:
        form = Profiles(profiles)
        return render(request, "home.html", {"term_courses": courses, "program_name": program_name, "form": form})

def courses(request):
    if not request.user.is_authenticated:
        return redirect("login")
    
    user = User.objects.get(username=request.user.username)
    account = Account.objects.get(user=user)
    courses = get_program_courses(account.program)
    user_program = account.program
    program_name = user_program.program_name
    
    profiles = []
    for profile in user_program.profiles.all():
        profiles.append((profile.profile_code, profile.profile_name))
    
    if request.method == "POST":
        if "t7" in request.POST:
            semester = request.POST.get("t7")
        
        elif "t8" in request.POST:
            semester = request.POST.get("t8")
        
        elif "t9" in request.POST:
            semester = request.POST.get("t9")
        
        term_courses = get_courses_term(user_program, semester, "free")
        print(f"data {str(term_courses)}")
        form = Profiles(profiles)
        return render(request, "home.html", {"term_courses": term_courses, 
                                             "program_name": name, 
                                             "termin": termin, 
                                             "form": form, 
                                             "course_tags": COURSE_TAGS}
                      )
    else:
        form = Profiles(profiles)
        return render(request, "home.html", {"term_courses": courses, "program_name": program_name, "form": form})

def setup(request):
    if not request.user.is_authenticated:
        return redirect("login")
    
    if request.method == "POST":
        form = ProgramForm(request.POST)
        if form.is_valid():
            program_code = request.POST.get("program").upper()
            program = Program.objects.filter(program_code=program_code)
            if program:
                user = User.objects.get(username=request.user.username)
                account = Account.objects.get(user=user)
                program = program[0]
                account.program = program
                account.save()
            return redirect("home")
                
    else:
        form = ProgramForm()

    return render(request, "setup.html", {"form": form})
