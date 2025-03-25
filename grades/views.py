from decimal import Decimal, ROUND_DOWN
from django.http import HttpResponse, HttpResponseBadRequest, Http404
from django.shortcuts import redirect, render
from django.db.models import Count, Q
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from . import models

# Create your views here.
@login_required
def index(request):
    assignments = models.Assignment.objects.all()
    values = { "assignments": assignments }
    return render(request, "index.html", values)

@login_required
def assignment(request, assignment_id):
    errors = {}
    if request.method == "POST":
        assignment_post_handler(request, assignment_id, errors)
    
    # get assignment based on id
    assignment = models.Assignment.objects.get(id=assignment_id)

    # get current user, as of HW3 it is just user g
    currentUser = request.user

    # get submission
    files = models.Submission.objects.filter(assignment=assignment).filter(author=currentUser).values()
    file = files[0].get("file", "")

    # get the assignment status
    status = get_assignment_status(currentUser, assignment)

    # get other needed fields
    totalSubmissions = assignment.submission_set.count()
    totalAssigned = currentUser.graded_set.filter(assignment=assignment).count()
    totalStudents = models.Group.objects.get(name="Students").user_set.count()
    isStudent = is_student(currentUser) if currentUser.is_authenticated else True
    isAdmin = currentUser.is_superuser
    values = {
        "id": assignment_id,
        "assignment": assignment,
        "totalSubmissions": totalSubmissions,
        "totalAssigned": totalAssigned,
        "totalStudents": totalStudents,
        "sub": file,
        "errors": errors,
        "isStudent": isStudent,
        "isAdmin": isAdmin,
        "status": status,
        "ontime": assignment.deadline > timezone.now(),
        "error": errors,
    }
    return render(request, "assignment.html", values)

def login_form(request):
    next = request.GET.get("next", "/profile/")

    if request.method == "POST":
        next = request.POST.get("next", "/profile/")

        # extracts username and password
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")

        # authenticates user, redirect if sucessful
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if url_has_allowed_host_and_scheme(next, None):
                return redirect(next)
            else:
                return redirect("/")
        else:
            return render(request, "login.html", {"error": "Username and password do not match", "next": next })
    

    return render(request, "login.html", {"next": next})

def logout_form(request):
    logout(request)
    return redirect("/profile/login/")

@login_required
def profile(request):
    # get all assignments
    assignments = models.Assignment.objects.all()

    # get current user, as of HW3 it is just user g
    currentUser = request.user
    isStudent = is_student(currentUser)

    totalAssigned = None
    totalGraded = None
    assignment_status = {}

    # changes dependent on user access
    if currentUser.is_superuser:
        # get all turned in assignments
        assigned = models.Submission.objects.all().values("assignment__title").annotate(num_assigned=Count("id"))
        totalAssigned = {item["assignment__title"]:item["num_assigned"] for item in assigned}

        # get all graded assignments
        graded = models.Submission.objects.filter(score__isnull=False).values("assignment__title").annotate(num_graded=Count("id"))
        totalGraded = {item["assignment__title"]:item["num_graded"] for item in graded}
    elif isStudent:
        assignment_status = get_grade_status(currentUser, assignments)
    else:
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
        "assignmentStatus": assignment_status,
        "user": currentUser,
        "isStudent": isStudent,
    }
    return render(request, "profile.html", values)

@login_required
def submissions(request, assignment_id):
    errors = {}
    # redirect for post requests
    if request.method == "POST":
        submissions_post_handler(request, assignment_id, errors)
    
    # get assignment based on id
    assignment = models.Assignment.objects.get(id=assignment_id)

    # get current user, as of HW3 it is just user g
    currentUser = request.user

    # get all submissions for this specific assignment
    userSubmissions = None
    if currentUser.is_superuser:
        userSubmissions = models.Submission.objects.order_by("author__username").filter(assignment=assignment)
    else:
        userSubmissions = currentUser.graded_set.filter(assignment=assignment).order_by("author__username").all()
    values = {
        "id": assignment_id,
        "assignment": assignment,
        "userSubmissions": userSubmissions,
        "errors": errors,
    }
    return render(request, "submissions.html", values)

@login_required
def show_upload(request, filename):
    # look up file with filename
    submission = models.Submission.objects.get(file=filename)
    currentUser = request.user
    file = submission.view_submission(currentUser)
    
    # test that file is a pdf
    if is_not_pdf(file):
        raise Http404

    response = HttpResponse(file.open())
    response["Content-Type"] = "application/pdf"
    response["Content-Disposition"] = f"attachment; filename='{file}'"

@login_required
def submissions_post_handler(request, assignment_id, errors):
    # check to see if user is a student
    if not is_ta(request.user):
        raise PermissionDenied
        
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
        submission.change_grade(request.user, grade)
        updated_submissions.append(submission)

    # save data
    if not errors:
        models.Submission.objects.bulk_update(updated_submissions, ["score"])
        print(errors)
        return redirect(f"/{assignment_id}/submissions/")

@login_required  
def assignment_post_handler(request, assignment_id, errors):
    # get assignment
    assignment = models.Assignment.objects.get(id=assignment_id)

    # check that deadline has not passed
    if assignment.deadline < timezone.now():
        return HttpResponseBadRequest

    # get submitted file
    submitted_file = request.FILES["submission"]

    # test the file size, reject if too large
    if submitted_file.size > (64 * 1024 * 1024):
        errors["file_size"] = "File size exceeded 64 MiB"
        return
    
    # test that file is a pdf
    if is_not_pdf(submitted_file):
        errors["file_type"] = "File type is not PDF"
        return

    # get Alice's submission if it exists, create it if it does not
    currentUser = request.user
    curr_submission, found = models.Submission.objects.filter(Q(author=currentUser)).get_or_create(
        assignment=assignment,
        author=currentUser,
        defaults={
            "grader": pick_grader(assignment),
            "file": submitted_file,
            "score": None,
        }
    )

    if found:
        curr_submission.file = submitted_file
        curr_submission.save()
    
    return redirect(f"/{assignment_id}/")

def is_student(user):
    return user.groups.filter(name="Students").exists()

def is_ta(user):
    return user.groups.filter(name="Teaching Assistant").exists()

def get_grade_status(student: User, assignments: models.Assignment):
    assignment_status = {}
    totalPossibleScore = 0
    totalAcquiredScore = 0

    # get every submission for the current student
    student_submissions_query = student.submission_set.all().values("assignment__id", "score")
    student_submissions = {sub["assignment__id"]:sub["score"] for sub in student_submissions_query}
    for a in assignments:
        # status depends on whether the assignment has been submitted, whether it was due, and whether it has been graded yet
        isSubmitted = a.id in student_submissions
        isDue = a.deadline < timezone.now()
        score = student_submissions.get(a.id)
        isGraded = True if score else False
        
        # check for each status using the bools above
        if isSubmitted and isGraded:
            assignment_status[a.id] = str((score / a.points) * 100) + "%" # score / total as a percent
            totalAcquiredScore = totalAcquiredScore + (score * a.weight)
            totalPossibleScore = totalPossibleScore + (a.points * a.weight)
        elif isSubmitted and not isGraded:
            assignment_status[a.id] = "Not Graded"
        elif not isSubmitted and not isDue:
            assignment_status[a.id] = "Not Due"
        elif not isSubmitted and isDue:
            assignment_status[a.id] = "Missing"
            totalPossibleScore = totalPossibleScore + (a.points * a.weight)
    
    # set the final score
    assignment_status["final_grade"] = "100%" if totalPossibleScore == 0 else str("{:.1f}".format((totalAcquiredScore / totalPossibleScore) * 100)) + "%"

    return assignment_status

def get_assignment_status(student: User, assignment: models.Assignment):
    # get the students submission, if it exists
    submission = student.submission_set.filter(assignment=assignment).first() # done to return None if submission does not exist

    # check if it was submitted, is due, and is graded
    isSubmitted = True if submission else False
    isDue = assignment.deadline < timezone.now()
    score = submission.score if isSubmitted else None
    isGraded = True if score else False

    # check for each status using the bools above
    if isSubmitted and isGraded:
        return f"Your submission, {str(submission.file)}, received {int(score)}/{assignment.points} points ({str((score / assignment.points) * 100)}%)" # score / total as a percent
    elif isSubmitted and not isGraded and isDue:
        return f"Your submission, {str(submission.file)}, is being graded"
    elif isSubmitted and not isDue:
        return f"Your current submission is {str(submission.file)}"
    elif not isSubmitted and not isDue:
        return "No current submission"
    elif not isSubmitted and isDue:
        return "You did not submit this assignment and received 0 points"
    
def pick_grader(assignment: models.Assignment):
    return models.Group.objects.get(name="Teaching Assistants").user_set.annotate(total_assigned=Count("graded_set")).order_by("total_assigned").first()

def is_not_pdf(file):
    return not file.endswith(".pdf") or not next(file.chunks()).startswith(b'%PDF-')