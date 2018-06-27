from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Doctor(models.Model):
    user = models.CharField(max_length=32, primary_key=True)
    pwd = models.CharField(max_length=32)
    sex = models.CharField(max_length=32)
    email = models.CharField(max_length=32)
    major = models.CharField(max_length=32,null=True)
    text = models.TextField()

class Family(models.Model):
    user = models.CharField(max_length=32, primary_key=True)
    pwd = models.CharField(max_length=32)
    sex = models.CharField(max_length=32)
    email = models.CharField(max_length=32)
    text = models.TextField()
    advice = models.TextField()

class Appointment(models.Model):
    family = models.ForeignKey(Family)
    doctor = models.ForeignKey(Doctor)
    time = models.CharField(max_length=32)
    response = models.CharField(max_length=32)

class Family_Doctor(models.Model):
    family = models.ForeignKey(Family)
    doctor_name = models.CharField(max_length=32)

