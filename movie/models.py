from django.db import models

# Create your models here.


class Movie(models.Model):
    ID = models.AutoField
    title = models.CharField(max_length=100)
    url = models.CharField(max_length=512)
    grade = models.CharField(max_length=512)
    duration = models.CharField(max_length=100)
    stock = models.IntegerField(default=100)
