from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.fields import IntegerField, TextField, TimeField
from django.db.models.fields.files import ImageField

# Create your models here.
class User(AbstractUser):
    pass
class Team(models.Model):
    teammate = models.ManyToManyField(User)
    team_name = models.CharField(max_length=128)
    zip_code = models.IntegerField()
    def __str__(self):
        return f"{self.id}- {self.team_name}"
class Event(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)
    time = TimeField(null=True, blank=True)
    event_name = models.CharField(max_length=64, blank=True, null=True)
    address = models.CharField(max_length=128, blank=True, null=True)
    city = models.CharField(max_length=128, blank=True, null=True)
    zip_code = models.IntegerField(blank=True, null=True) 
    attendees = models.ManyToManyField(User)
    description = models.TextField()
class AboutMe(models.Model):
    about_user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=128)
    age = models.IntegerField()
    image = ImageField(upload_to='documents/image')
    self_blurb = TextField()
    zip_code = IntegerField()