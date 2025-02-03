from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    title: str = models.CharField(max_length=255)
    description: str = models.TextField()
    instructor: str = models.CharField(max_length=255)
    duration: str = models.CharField(max_length=50)

    def __str__(self):
        return self.title

class Enrollment(models.Model):
    student: User = models.ForeignKey(User, on_delete=models.CASCADE)
    course: Course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrollment_date: models.DateField = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_name} enrolled in {self.course.title}"

    class Meta:
        unique_together = ("student", "course")
