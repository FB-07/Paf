from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from ..models import UsersProfile
from django.contrib.auth.models import User
from ..decorators import admin_required

@admin_required
def admin_reports(request):
    return render(request, "admin/reports.html")
