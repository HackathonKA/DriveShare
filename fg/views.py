from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseForbidden, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import *

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

class CreateCarpool(LoginRequiredMixin, TemplateView):
    template_name = "fg/newCarpool.html"

    def post(self, request):
        cp = Carpool()
        cp.name = request.POST["title"]
        cp.desc = request.POST["desc"]
        cp.loc_a = request.POST["locA"]
        cp.loc_b = request.POST["locB"]
        cp.active = True
        cp.save()

        # Link to creating user
        m = Membership()
        m.user = request.user
        m.pool = cp
        m.save()

        return redirect("dashboard")

# Create your views here.
def home(request):
    return render(request, "fg/home.html", {"path":["Home",]})

def register(request):
    return render(request, "registration/register.html", {"path":["User", "Register",]})

def helpview(request):
    return render(request, "misc/help.html", {"path":["Help",]})

def impressum(request):
    return render(request, "misc/impressum.html", {"path":["Impressum",]})

@login_required
def dashboard(request):
    return render(request, "fg/dashboard.html", {"path":["Dashboard",]})

@login_required
def profile(request, num):
    user = get_object_or_404(User, pk=num)
    return render(request, "fg/profile.html", {"path":["User", "Profile",], "user": user})

@login_required
def carpool(request, id, day="today"):
    user = request.user
    ms = user.membership_set.all()
    match = False
    for m in ms:
        if m.pool.pk == id:
            match=True
            break
        else:
            print(str(m.pool.pk) + " <> " + str(id))


    if not match:
        return HttpResponseForbidden("No Permission!")

    carpool = get_object_or_404(Carpool, pk=id)
    if day == "today":
        data = carpool.getDriverConfigurationForToday()
    elif day == "next":
        data = carpool.getDriverConfigurationForTomorrow()
    else:
        raise Http404


    return render(request, "fg/carpool.html", {"carpool": carpool, "driversToday": data})
