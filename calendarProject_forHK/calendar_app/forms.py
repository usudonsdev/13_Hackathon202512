from django.forms import ModelForm
from .models import *

class CreateAccountForm(ModelForm):
    class Meta:
        model = UserID
        fields=["id","password"]