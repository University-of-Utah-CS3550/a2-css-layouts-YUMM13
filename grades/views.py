from decimal import Decimal, ROUND_DOWN
from django.shortcuts import redirect, render
from django.db.models import Count
from . import models

# Create your views here.
def index(request):
    assignments = models.Assignment.objects.all()
    values = { "assignments": assignments }
    return render(request, "index.html", values)

def assignment(request, assignment_id):
    # get assignment based on id
    assignment = models.Assignment.objects.get(id=assignment_id)

    # get current user, as of HW3 it is just user g
    currentUser = models.User.objects.get(username="g")

    # get other needed fields
    totalSubmissions = assignment.submission_set.count()
    totalAssigned = currentUser.graded_set.filter(assignment=assignment).count()
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
    # get all assignments
    assignments = models.Assignment.objects.all()

    # get current user, as of HW3 it is just user g
    currentUser = models.User.objects.get(username="g")

    # get the submissions assigned to the current user, turn it into a dictionary
    assigned = currentUser.graded_set.values("assignment__title").annotate(num_assigned=Count("id"))
    totalAssigned = {item["assignment__title"]:item["num_assigned"] for item in assigned}

    # get the submissions graded by the current user, turn it into a dictionary
    graded = currentUser.graded_set.filter(score__isnull=False).values("assignment__title").annotate(num_graded=Count("id"))
    totalGraded = {item["assignment__title"]:item["num_graded"] for item in graded}
    values = {
        "assignments": assignments,
        "totalAssigned": totalAssigned,
        "totalGraded": totalGraded,
    }
    return render(request, "profile.html", values)

def submissions(request, assignment_id):
    errors = {}
    # redirect for post requests
    if request.method == "POST":
        updated_submissions = []
        for key in request.POST:
            # skip if it is not a grade input
            if "grade-" not in key:
                continue
            # grab the grade
            gradeID = int(key.removeprefix("grade-"))
            
            # check that grade is for a valid submission
            try:
                submission = models.Submission.objects.get(id=gradeID)
                gradeLookup = request.POST[key]
            except KeyError:
                errors[str(gradeID)] = "The submission ID does not exist for a grade given"
                continue

            try:
                # make sure that inputted grade is a number
                grade = None
                if gradeLookup != "":
                    grade = Decimal(gradeLookup).quantize(Decimal('.01'), rounding=ROUND_DOWN)

                # check to see if the grade is in bounds
                total = submission.assignment.weight
                if grade < 0:
                    errors[str(gradeID)] = "Inputted grade is less than 0"
                    continue
                elif grade > total:
                    errors[str(gradeID)] = "Inputted grade is greater than assignment total"
                    continue
            except TypeError:
                errors[str(gradeID)] = "Inputted grade is not a number"
                continue
            # get the submission from the db and set it
            submission.score = grade
            updated_submissions.append(submission)

        # save data
        if not errors:
            models.Submission.objects.bulk_update(updated_submissions, ["score"])
            print(errors)
            return redirect(f"/{assignment_id}/submissions/")
    
    # get assignment based on id
    assignment = models.Assignment.objects.get(id=assignment_id)

    # get current user, as of HW3 it is just user g
    currentUser = models.User.objects.get(username="g")

    # get all submissions for this specific assignment
    userSubmissions = currentUser.graded_set.filter(assignment=assignment).order_by("author__username").all()
    values = {
        "id": assignment_id,
        "assignment": assignment,
        "userSubmissions": userSubmissions,
        "errors": errors,
    }
    print(errors)
    return render(request, "submissions.html", values)
