from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

# Create your views here.
def home(request):
    return render(request, "fg/home.html", {"path":["Home",]})

def register(request):
    return render(request, "registration/register.html", {"path":["User", "Register",]})

@login_required
def dashboard(request):
    return render(request, "fg/dashboard.html", {"path":["Dashboard",]})

@login_required
def profile(request, id):
    user = get_object_or_404(User, pk=id)
    return render(request, "fg/profile.html", {"path":["User", "Profile",], "user": user})