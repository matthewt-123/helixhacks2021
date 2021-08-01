from django.forms import ModelForm
from .models import Team, AboutMe, Event
from django import forms
from django.contrib.admin import widgets

forms.DateInput.input_type="date"
forms.TimeInput.input_type="time" 

class TeamForm(ModelForm):
    class Meta:
        model = Team
        fields = ['team_name', 'zip_code']
class AboutForm(ModelForm):
    class Meta:
        model = AboutMe
        fields = ['first_name', 'age', 'image', 'self_blurb', 'zip_code']
class EventForm(ModelForm):
    class Meta:
        model = Event
        fields = ['event_name', 'date', 'time', 'address', 'city', 'zip_code', 'description']
    date = forms.DateInput()
    time = forms.TimeInput()