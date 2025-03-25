from django.db import models
from django.contrib.auth.models import User, Group
from django.core.exceptions import PermissionDenied

# Create your models here.
class Assignment(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    deadline = models.DateTimeField()
    weight = models.IntegerField(default=0)
    points = models.IntegerField(default=0)

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    grader = models.ForeignKey(User, related_name='graded_set', on_delete=models.SET_NULL, null=True)
    file = models.FileField(null=True)
    score = models.DecimalField(default=0, decimal_places=2, max_digits=4, null=True)

    def change_grade(self, user, grade):
        if self.grader != user:
            raise PermissionDenied
        self.score = grade

    def view_submission(self, user: User):
        isAuthor = user == self.author
        isGrader = user == self.grader
        isAdmin = user.is_superuser

        if not isAuthor and not isGrader and not isAdmin:
            raise PermissionDenied
        
        return self.file