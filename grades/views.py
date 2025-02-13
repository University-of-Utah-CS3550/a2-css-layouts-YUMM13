from django.shortcuts import render
from . import models

# Create your views here.
def index(request):
    assignments = models.Assignment.objects.all()
    values = { "assignments": assignments }
    return render(request, "index.html", values)

def assignment(request, assignment_id):
    assignment = models.Assignment.objects.get(id=assignment_id)
    currentUser = models.User.objects.get(username="g")
    totalSubmissions = assignment.submission_set.count()
    totalAssigned = currentUser.graded_set.count()
    totalStudents = models.Group.objects.get(name="Students").user_set.count()
    values = {
        "id": assignment_id,
        "assignment": assignment,
        "totalSubmissions": totalSubmissions,
        "totalAssigned": totalAssigned,
        "totalStudents": totalStudents,
    }
    return render(request, "assignment.html", values)

def login_form(request):
    return render(request, "login.html")

def profile(request):
    return render(request, "profile.html")

def submissions(request, assignment_id):
    return render(request, "submissions.html")
