from django.forms import ModelForm
from django import forms
from .models import *

class CreateAccountForm(ModelForm):
    class Meta:
        model = UserID
        fields=["id","password"]

class CreatePlanForm(forms.Form):
    name = forms.CharField(max_length=100)
    private = forms.ChoiceField(choices=[(0, "公開"), (1, "非公開")])
    year = forms.IntegerField()
    month = forms.IntegerField()
    day = forms.IntegerField()
    start_hour = forms.IntegerField()
    start_minute = forms.IntegerField()
    end_hour = forms.IntegerField()
    end_minute = forms.IntegerField()
    memo = forms.CharField(widget=forms.Textarea, required=False)


class CreateRoutineForm(forms.Form):
    names = forms.CharField(max_length=100)
    private = forms.ChoiceField(choices=[(0, "公開"), (1, "非公開")])
    day_of_week = forms.ChoiceField(choices=[(0,"日曜"),(1,"月曜"),(2,"火曜"),(3,"水曜"),(4,"木曜"),(5,"金曜"),(6,"土曜")])
    start_hour = forms.IntegerField()
    start_minute = forms.IntegerField()
    end_hour = forms.IntegerField()
    end_minute = forms.IntegerField()
    
class SearchSlotForm(forms.Form):
    names = forms.CharField(max_length=100)
    period_start = forms.DateField()
    period_end = forms.DateField()
    desired_start = forms.TimeField()
    desired_end = forms.TimeField()
    duration_hours = forms.IntegerField()
    duration_minutes = forms.IntegerField()
    
    