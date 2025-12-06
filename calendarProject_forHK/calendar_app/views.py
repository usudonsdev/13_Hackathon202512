from django.shortcuts import render,redirect,get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from .models import *
from .forms import *
# Create your views here.

class IndexView(LoginRequiredMixin,View):
    def get(self,request):
        return render(request,"calendar_app/index.html")

class AccountCreateView(View):
    def get(self,request):
        form=CreateAccountForm()
        return render(request,"calendar_app/account_create.html",{"form":form})
    def post(self,request):
        form=CreateAccountForm(request.POST)
        if form.is_valid():
            id=form.cleaned_data.get('id')
            password=form.cleaned_data.get('password')
            form.save()
            User.objects.create_user(id,"",password)
            record=UserID.objects.get(id=id)
            record.password="password"
            record.save()
            return redirect("calendar_app:index")
        return render(request,"account/create/index.html",{"form":form})
        
index=IndexView.as_view()
account_create=AccountCreateView.as_view()