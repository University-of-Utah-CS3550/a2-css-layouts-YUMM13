from django.shortcuts import render
from . import models

# Create your views here.
def index(request):
    assignments = models.Assignment.objects.all()
    values = { "assignments": assignments }
    return render(request, "index.html", values)

def assignment(request, assignment_id):
    return render(request, "assignment.html")

def login_form(request):
    return render(request, "login.html")

def profile(request):
    return render(request, "profile.html")

def submissions(request, assignment_id):
    return render(request, "submissions.html")
