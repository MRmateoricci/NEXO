from django.db import models

# Create your models here.
class Project(models.Model):
    name = models.CharField(max_length=100)


class Taks(models.Model):
    title = models.CharField(max_length=100)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    description = models.TextField()
    