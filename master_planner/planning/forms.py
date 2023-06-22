from django import forms
from django.contrib.auth.forms import forms

class ProgramForm(forms.Form):
    program = forms.CharField(label="", widget=forms.TextInput(attrs={"placeholder": "Program code"}))
    
class ProfileCourses(forms.Form):
    profile = forms.CharField()
    
class Profiles(forms.Form):
    profiles = forms.ChoiceField(choices=())
    def __init__(self, profiles=None, *args, **kwargs):
        super(Profiles, self).__init__(*args, **kwargs)
        if profiles:
            self.fields['profiles'].choices = profiles
            
    """    
    A = "A"
    B = "B"
    TYPES = [
        (A, "A_X"),
        (B, "B_X")
    ]
    """