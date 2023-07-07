"""
URL configuration for master_planner project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
import accounts.views as account
import planning.views as planning
from .api import api

urlpatterns = [
    path('', planning.home),
    path('setup/', planning.setup, name="setup"),
    path('', include("django.contrib.auth.urls")),
    path('register/', account.register, name="register"),
    path('home/', planning.home, name="home"),
    path('admin/', admin.site.urls, name="admin"),
    path('api/', api.urls)
    
]
