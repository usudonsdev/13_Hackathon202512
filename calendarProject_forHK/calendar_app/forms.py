from django.forms import ModelForm
from .models import *

class CreateAccountForm(ModelForm):
    class Meta:
        model = UserID
        fields=["id","password"]

class CreatePlanForm(ModelForm):
    class Meta:
        model = Plan
        fields=["name","private","year","month","day","start_hour","start_minute","end_hour","end_minute","memo"]