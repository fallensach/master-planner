from django import forms
from django.contrib.auth.forms import forms, UserCreationForm
from .models import Account
from planning.models import Program

# class RegisterForm():
#     username = forms.CharField(label="Username", max_length=100)
#     email = forms.EmailField()
#     password = forms.CharField(widget=forms.PasswordInput())

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = Account
        fields = ("username", "password1", "password2", "program")
