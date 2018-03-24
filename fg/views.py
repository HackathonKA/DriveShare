from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    return render(request, "fg/home.html", {"path":["Home",]})

@login_required
def dashboard(request):
    return render(request, "fg/dashboard.html", {})
