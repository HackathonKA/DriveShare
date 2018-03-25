from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseForbidden, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import *

from django.views.generic import TemplateView
from django.views import View
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

class LeaveCarpool(LoginRequiredMixin, View):
    def get(self, request):
        raise Http404

    def post(self, request, id):
        cp = get_object_or_404(Carpool, pk=id)
        m = get_object_or_404(Membership, user=request.user, pool=cp)
        m.delete()
        return redirect("dashboard")

class AddToCarpool(LoginRequiredMixin, View):
    def get(self, request):
        raise Http404

    def post(self, request, id):
        cp = get_object_or_404(Carpool, pk=id)

        m = get_object_or_404(Membership, user=request.user, pool=cp)
        # Return 404 if user is not in the actual pool TODO: Use right error code ^^
        usr = request.POST["username"]
        userToAdd = get_object_or_404(User, username=usr)
        nm = Membership()
        nm.user = userToAdd
        nm.pool = cp
        nm.save()
        return redirect("carpoolOverview", id)

class UpdateCarpool(LoginRequiredMixin, View):
    def get(self, request):
        raise Http404

    def post(self, request, id):
        cp = get_object_or_404(Carpool, pk=id)
        m = get_object_or_404(Membership, user=request.user, pool=cp)

        lst = request.POST.getlist("days")
        m.days = lst
        m.save()

        return redirect("carpoolOverview", id)

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
            member = m
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

    return render(request, "fg/carpool.html", {"carpool": carpool, "driversToday": data, "myMember": member})
