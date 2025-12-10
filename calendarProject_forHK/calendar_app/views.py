from django.shortcuts import render,redirect,get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from .models import *
from .forms import *
from datetime import datetime, timedelta, timezone
from time import time
from django.utils import timezone
#import datetime
# Create your views here.

class IndexView(LoginRequiredMixin,View):
    def get(self,request):

        now = timezone.now()
        next_plan_queryset = Plan.objects.filter(start_datetime__gte=now, user=str(request.user)).order_by('start_datetime')[:20]
        before_plan_queryset = Plan.objects.filter(start_datetime__lte=now, user=str(request.user)).order_by('-start_datetime')[:20]
        #print(next_plan_queryset[0])
        #print(len(before_plan_queryset))
        events = [[0 for j in range(3)] for i in range(50)]
        event_name=[0 for j in range(50)]
        event_start=[0 for j in range(50)]
        event_end=[0 for j in range(50)]

        for i in range(20):
            if(i<len(next_plan_queryset)):
                event_name[i]=next_plan_queryset[i].name
                event_start[i]=str(next_plan_queryset[i].start_datetime).replace(' ','T')[:-6]
                event_end[i]=str(next_plan_queryset[i].end_datetime).replace(' ','T')[:-6]
            else:
                event_name[i]="null"
                event_start[i]="2015-12-12T23:00:00"
                event_end[i]="2015-12-12T23:30:00"

        for i in range(20,40):
            if(i<len(before_plan_queryset)):
                event_name[i]=before_plan_queryset[i].name
                event_start[i]=str(before_plan_queryset[i].start_datetime).replace(' ','T')[:-6]
                event_end[i]=str(before_plan_queryset[i].end_datetime).replace(' ','T')[:-6]
            else:
                event_name[i]="null"
                event_start[i]="2015-12-12T23:00:00"
                event_end[i]="2015-12-12T23:30:00"

        return render(request,"calendar_app/index.html",{"event_name":event_name,"event_start":event_start,"event_end":event_end})

    def post(self,request):
        name=request.POST['event-title']
        event_start=request.POST['event-start']+"+0900"
        event_end=request.POST['event-end']+"+0900"
        private=request.POST['private']
        event_memo=request.POST['event-memo']
        #print(name+"\n"+event_start+"\n"+event_end+"\n"+private+"\n"+event_memo+"\n")
        if(private=="private"):
            private=1
        else:
            private=0
        Plan.objects.create(
            user=str(request.user),
            name=name,
            memo=event_memo,
            private=private,
            start_datetime=event_start,
            end_datetime=event_end,
            )


        return redirect("calendar_app:index")

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
        

class PlanCreateView(View):
    def get(self,request):
        form=CreatePlanForm()
        return render(request,"calendar_app/create_plan.html",{"form":form})
    def post(self,request):
        form=CreatePlanForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            start_dt = datetime(
                cd['year'], cd['month'], cd['day'], cd['start_hour'], cd['start_minute'],
            )
            end_dt = datetime(
                cd['year'], cd['month'], cd['day'], cd['end_hour'], cd['end_minute'],
            )
            Plan.objects.create(
                user=str(request.user),
                name=cd['name'],
                memo=cd['memo'],
                private=cd['private'],
                start_datetime=start_dt,
                end_datetime=end_dt,
            )
            return redirect("calendar_app:index")
        return render(request,"calendar_app/create_plan.html",{"form":form})

class RoutineCreateView(View):
    def get(self,request):
        return render(request,"calendar_app/create_routine.html",)
    def post(self,request):
        name=request.POST['event-title']
        event_start=request.POST['event-start']
        event_end=request.POST['event-end']
        private=request.POST['private']
        day_of_week=request.POST['day-of-week']
        event_memo=request.POST['event-memo']
        if(private=="private"):
            private=1
        else:
            private=0
        Routine.objects.create(
            user = str(request.user),
            name = name,
            day_of_week =day_of_week,
            private = private,
            start_time = event_start,
            end_time = event_end,
        )
        return redirect("calendar_app:index")
    
class SearchView(View):
    def get(self, request):
        #form = SearchSlotForm()

        return render(request, "calendar_app/Scheduling_Assist_System.html")
    def post(self, request):
        #form = SearchSlotForm(request.POST)
        #cd = form.cleaned_data
        assist_title=request.POST['assist-title']
        period_start = request.POST['assist-start-datetime']
        period_start = datetime.strptime(period_start, "%Y-%m-%d").date()
        period_end = request.POST['assist-end-datetime']
        period_end = datetime.strptime(period_end, "%Y-%m-%d").date()
        desired_start = request.POST['assist-start-time']
        desired_start = datetime.strptime(desired_start, "%H:%M").time()
        desired_end = request.POST['assist-end-time']
        desired_end = datetime.strptime(desired_end, "%H:%M").time()
        my_user = str(request.user)
        target_users = request.POST.getlist('users')
        duration = timedelta(
            hours = int(request.POST['assist-duration-h']), minutes = int(request.POST['assist-duration-m']),
        )
        
        results = []
        current_date = period_start
        while current_date <= period_end:
            day_start = datetime.combine(current_date, desired_start)
            day_end = datetime.combine(current_date, desired_end)
            t = day_start
            while t + duration <= day_end:
                conflict_self_plan = Plan.objects.filter(
                    start_datetime__lt = t + duration,
                    end_datetime__gt = t,
                    user = my_user,
                ).exists()
                
                routine_self = Routine.objects.filter(user = my_user)
                
                conflict_self_routine = False
                
                for r in routine_self:
                    if current_date.weekday() != ((r.day_of_week + 6) % 7):
                        continue
                    routine_start_self = datetime.combine(current_date, r.start_time)
                    routine_end_self = datetime.combine(current_date, r.end_time)
                    
                    if not ((routine_start_self < t + duration) and (routine_end_self > t)):
                        conflict_self_routine = False
                    else:
                        conflict_self_routine = True
                        break
                    
                conflict_members_routine = False
                    
                if target_users:
                    conflict_members_plan = Plan.objects.filter(
                        start_datetime__lt = t + duration,
                        end_datetime__gt = t,
                        user__in = target_users,
                        private = 0,
                    ).exists()
                    
                    routine_members = Routine.objects.filter(user__in=target_users)
                    
                    for others in routine_members:
                        if current_date.weekday() != ((others.day_of_week + 6) % 7):
                            continue
                        routine_start_members = datetime.combine(current_date, others.start_time)
                        routine_end_members = datetime.combine(current_date, others.end_time)
                        
                        if not ((routine_start_members < t + duration) and (routine_end_members > t)):
                            conflict_members_routine = False
                        else:
                            conflict_members_routine = True
                            break
                        
                else:
                    conflict_members_plan = False
                
                if not ((conflict_self_plan) or (conflict_members_plan) or (conflict_self_routine) or (conflict_members_routine)):
                    results.append([t,t+duration])
                t = t + timedelta(minutes=30)
            current_date = current_date + timedelta(days=1)
        return redirect("calendar_app:index")
            

            
            
        
class AccountViewView(View):
    def get(self,request):
        user_name = str(request.user)
        return render(request,"calendar_app/account.html",{"user_name": user_name})
 




index=IndexView.as_view()
account_create=AccountCreateView.as_view()
plan_create=PlanCreateView.as_view()
routine_create=RoutineCreateView.as_view()
search_view=SearchView.as_view()
account_view=AccountViewView.as_view()
