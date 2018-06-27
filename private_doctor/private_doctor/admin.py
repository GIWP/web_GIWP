from django.contrib import admin

# Register your models here.
from private_doctor import models
admin.site.register(models.Doctor)
admin.site.register(models.Family)
admin.site.register(models.Family_Doctor)
admin.site.register(models.Appointment)