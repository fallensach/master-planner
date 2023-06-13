from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from .models.program import Program

def index(request):
    prog = Program("6CYYY")
    prog.save()
    print(prog.program_code)
    return HttpResponse("epic new site")