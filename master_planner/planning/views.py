from django.shortcuts import render, redirect
from .forms import ProgramForm, Profiles
from planning.models import Program, Profile, Schedule, Scheduler, get_courses_term
from accounts.models import Account
from django.contrib.auth.models import User


# def get_data(profil):
#     return {"semester": {"period1" : [{"course_code": "tata24", "details": []}]}}


COURSE_TAGS = {
                "Kurskod": "",
                "Kursnamn": "",
                "Hp": "",
                "Block": "",
                "Nivå": "",
                "Vof": "",
                "Detaljer": "",
                }


def home(request):
    if not request.user.is_authenticated:
        return redirect("login")
    
    account = Account.objects.get(user=request.user)

    if account.program is None:
        return redirect("overview")

    user_program = account.program
    profiles = [(profile.profile_code, profile.profile_name) for profile in user_program.profiles.all()]
    profiles_dict = dict(profiles) 
    
    if request.method == "POST":
        if "pick_profile" in request.POST:
            profile_code = request.POST["profiles"]
            profile_name = Profile.objects.get(profile_code=profile_code).profile_name
            form = Profiles(profiles)
            semester = 7
        else:
            profile_code = request.POST.get("profile_code")
            
        form = Profiles(profiles)
        profile_name = profiles_dict[profile_code]
        profile = Profile.objects.get(profile_code=profile_code)
        semester_courses = get_courses_term(program=account.program, semester=semester, profile=profile)
            
    else:
        profile_code = "free"
        profile = Profile.objects.get(profile_code=profile_code)
        profile_name = profile.profile_name
        semester_courses = get_courses_term(program=account.program, semester=7, profile=profile)
        form = Profiles(profiles)
    
    return render(request, "home.html", {"period_scheduler": semester_courses, 
                                             "program_name": user_program, 
                                             "termin": "Termin 7", 
                                             "form": form, 
                                             "profile_picked": True, 
                                             "profile_code": profile_code, 
                                             "profile_name": profile_name, 
                                             "course_tags": COURSE_TAGS,
                                             "home_p": "p-3",
                                             "home_bg": "bg-white/25",
                                             "home_highlight": "bg-white/25 p-3 rounded-lg"}
                                         )
