from django import forms
from django.contrib.auth.forms import forms

class RegisterForm(forms.Form):
    username = forms.CharField(label="Username", max_length=100)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())