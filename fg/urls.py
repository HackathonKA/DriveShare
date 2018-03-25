"""DriveShare URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.contrib.auth import views as auth_views
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('dashboard/', views.dashboard, name="dashboard"),
    path('help/', views.helpview, name="help"),
    path('impressum/', views.impressum, name="impressum"),

    path('carpool/create', views.CreateCarpool.as_view(), name="createCarpool"),
    path('carpool/leave/<int:id>', views.LeaveCarpool.as_view(), name="leaveCarpool"),
    path('carpool/update/<int:id>', views.UpdateCarpool.as_view(), name="changeCarpoolSettings"),
    path('carpool/add/<int:id>', views.AddToCarpool.as_view(), name="addToCarpool"),
    path('carpool/<int:id>', views.carpool, name="carpoolOverview"),
    path('carpool/<int:id>/<day>', views.carpool, name="carpoolOverview"),


    # Auth stuff
    path('user/login/', auth_views.LoginView.as_view(), name="login"),
    path('user/logout/', auth_views.LogoutView.as_view(), name="logout"),
    path('user/register/', views.register, name="register"),
    path('user/<int:num>/profile/', views.profile, name="profile"),
]
