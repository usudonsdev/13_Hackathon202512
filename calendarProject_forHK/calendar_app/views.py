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
from .services.googleCalendar_interface import CalendarService
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
import os
from calendar_app.services import friend


# Create your views here.

@login_required
def google_calendar_auth_start(request):
    """
    Starts the Google Calendar API authentication process.
    """
    calendar_service = CalendarService()
    authorization_url, state = calendar_service.get_authorization_url()
    request.session['oauth_state'] = state
    return HttpResponseRedirect(authorization_url)

@login_required
def google_calendar_auth_callback(request):
    """
    Handles the callback from the Google Calendar API authentication.
    """
    state = request.session.pop('oauth_state', '')
    if state != request.GET.get('state'):
        return redirect("calendar_app:index")  # CSRF warning

    calendar_service = CalendarService()
    try:
        credentials = calendar_service.fetch_token(request.build_absolute_uri(), state)
    except Exception as e:
        # Handle case where user denies access
        return redirect("calendar_app:index")

    request.session['google_oauth_credentials'] = credentials.to_json()

    events = calendar_service.list_events(credentials)

    for event in events:
        summary = event.get('summary')
        description = event.get('description', '')
        start = event.get('start', {}).get('dateTime')
        end = event.get('end', {}).get('dateTime')

        if not all([summary, start, end]):
            continue  # Skip events without a summary, start or end time

        start_datetime = datetime.fromisoformat(start)
        end_datetime = datetime.fromisoformat(end)

        # Create a new Plan object
        Plan.objects.create(
            user=str(request.user),
            name=summary,
            memo=description,
            private=1,  # Default to private
            start_datetime=start_datetime,
            end_datetime=end_datetime,
        )

    return redirect("calendar_app:index")

class IndexView(LoginRequiredMixin,View):
    def get(self,request):

        now = timezone.now()
        next_plan_queryset = Plan.objects.filter(start_datetime__gte=now, user=str(request.user)).order_by('start_datetime')[:20]
        before_plan_queryset = Plan.objects.filter(start_datetime__lte=now, user=str(request.user)).order_by('-start_datetime')[:20]
        #print(next_plan_queryset[0])
        print(len(before_plan_queryset))
        #events = [[0 for j in range(3)] for i in range(50)]
        event_name=[0 for j in range(50)]
        event_start=[0 for j in range(50)]
        event_end=[0 for j in range(50)]
        event_category = 'meeting'
        #print(event_category)

        for i in range(20):
            if(i<len(next_plan_queryset)):
                event_name[i]=next_plan_queryset[i].name
                event_start[i]=str(next_plan_queryset[i].start_datetime+timedelta(hours=9)).replace(' ','T')[:-6]
                event_end[i]=str(next_plan_queryset[i].end_datetime+timedelta(hours=9)).replace(' ','T')[:-6]
                #print(next_plan_queryset[i].start_datetime)
                #print(event_start[i])
            else:
                event_name[i]="null"
                event_start[i]="2015-12-12T23:00:00"
                event_end[i]="2015-12-12T23:30:00"

        for i in range(20,40):
            if(i<len(before_plan_queryset)+20):
                event_name[i]=before_plan_queryset[i-20].name
                event_start[i]=str(before_plan_queryset[i-20].start_datetime+timedelta(hours=9)).replace(' ','T')[:-6]
                event_end[i]=str(before_plan_queryset[i-20].end_datetime+timedelta(hours=9)).replace(' ','T')[:-6]
                #print(event_name[i])
            else:
                event_name[i]="null"
                event_start[i]="2015-12-12T23:00:00"
                event_end[i]="2015-12-12T23:30:00"


        return render(request,"calendar_app/index.html",{"event_name":event_name,"event_start":event_start,"event_end":event_end,"event_category":event_category})

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
        return render(request,"calendar_app/account_create.html",{"form":form})
        
class PlanCreateView(LoginRequiredMixin,View):
    def get(self,request):
        title = request.GET.get("title")
        start = request.GET.get("start")
        end = request.GET.get("end")
        if not title:
            title = ""
        if start:
            start = datetime.strptime(start, "%Y年%m月%d日%H:%M")
            start = start.strftime("%Y-%m-%dT%H:%M")
        else:
            start = None
            
        if end:
            end = datetime.strptime(end, "%Y年%m月%d日%H:%M")
            end = end.strftime("%Y-%m-%dT%H:%M")
        else:
            end = None
            
        return render(request,"calendar_app/create_plan.html",{"start_init":start, "end_init":end, "title_init":title})
    def post(self,request):
        name=request.POST['event-title']
        datetime_start=request.POST['event-start']
        datetime_end=request.POST['event-end']
        private=request.POST['visibility']
        event_memo=request.POST['event-memo']
        if(private=="private"):
            private=1
        else:
            private=0
        Plan.objects.create(
            user = str(request.user),
            name = name,
            start_datetime = datetime_start,
            end_datetime = datetime_end,
            private = private,
            memo = event_memo,
        )
        
        return redirect("calendar_app:index")

class RoutineCreateView(LoginRequiredMixin,View):
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
    
class SearchView(LoginRequiredMixin,View):
    def get(self, request):
        #form = SearchSlotForm()

        return render(request, "calendar_app/Scheduling_Assist_System.html")
    def post(self, request):
        #form = SearchSlotForm(request.POST)
        #cd = form.cleaned_data
        action = request.POST.get("action")
        assist_name = request.POST.get("assist-title")
        period_start = request.POST.get("assist-start-datetime")
        period_end = request.POST.get("assist-end-datetime")
        if action == "retry":
            period_start = datetime.strptime(period_start, "%Y年%m月%d日").date()
            period_end = datetime.strptime(period_end, "%Y年%m月%d日").date()
        else:
            period_start = datetime.strptime(period_start, "%Y-%m-%d").date()
            period_end = datetime.strptime(period_end, "%Y-%m-%d").date()
        desired_start = request.POST.get("assist-start-time")
        desired_start = datetime.strptime(desired_start, "%H:%M").time()
        desired_end = request.POST.get("assist-end-time")
        desired_end = datetime.strptime(desired_end, "%H:%M").time()
        my_user = str(request.user)
        target_users = request.POST.getlist('users')
        
        duration = timedelta(
            hours = int(request.POST.get("assist-duration-h")), minutes = int(request.POST.get("assist-duration-m")),
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
                    
                if any(target_users):
                    conflict_members_plan = Plan.objects.filter(
                        start_datetime__lt = t + duration,
                        end_datetime__gt = t,
                        user__in = target_users,
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
        if action == "retry":
            shown_slots = request.POST.getlist("shown_slots")
            excluded = set(shown_slots)
            filter = []
            for start, end in results:
                key = f"{start.strftime('%Y-%m-%dT%H:%M')}|{end.strftime('%Y-%m-%dT%H:%M')}"
                if not key in excluded:
                    filter.append([start, end])
            filter_size = len(filter)
            if filter_size >= 5:
                selected_filter = []
                index_medium = int((filter_size-1)/2)
                index_fq = int(index_medium/2)
                index_tq = int(((filter_size-1)-index_medium)/2 + index_medium)
                selected_filter.append(results[0])
                selected_filter.append(results[index_fq])
                selected_filter.append(results[index_medium])
                selected_filter.append(results[index_tq])
                selected_filter.append(results[filter_size-1])
                results = selected_filter
            return render(request, "calendar_app/Scheduling_Assist_System.html", {"results":results, "assist_name":assist_name})
        else:
            if not any(target_users):
                results_size = len(results)
                if results_size >= 5:
                    selected_results = []
                    index_medium = int((results_size-1)/2)
                    index_fq = int(index_medium/2)
                    index_tq = int(((results_size-1)-index_medium)/2 + index_medium)
                    selected_results.append(results[0])
                    selected_results.append(results[index_fq])
                    selected_results.append(results[index_medium])
                    selected_results.append(results[index_tq])
                    selected_results.append(results[results_size-1])
                    results = selected_results
                return render(request, "calendar_app/Scheduling_Assist_System.html", {"results":results, "assist_name":assist_name, "assist_start_date":period_start, "assist_end_date":period_end, "assist_start_time":desired_start, "assist_end_time":desired_end, "assist_duration_h":request.POST.get("assist-duration-h"), "assist_duration_m":request.POST.get("assist-duration-m")})
        return redirect("calendar_app:index")
            

            
            
class AccountViewView(LoginRequiredMixin,View):
    def get(self,request):
        User=UserID.objects.get(id=str(request.user))
        print("名前:"+str(User.name))
        if(str(User.name)=="None"):
            user_name=str(request.user)
        else:
            user_name=str(User.name)
        user_id=str(request.user)
        bio=str(User.introduce)
        icon=User.icon
        now = timezone.now()
        service = friend.friendService()
        friends=service.get_friend_list(str(request.user))
        #print(str(len(friends)))
        next_plan_queryset = Plan.objects.filter(start_datetime__gte=now, user=str(request.user)).order_by('start_datetime')[:2]
        Plans=[0]*4
        if(len(next_plan_queryset)>=1):
            Plans[0]=next_plan_queryset[0].start_datetime
            Plans[1]=next_plan_queryset[0].name
        else:
            Plans[0]=""
            Plans[1]=""

        if(len(next_plan_queryset)>=2):
            Plans[2]=next_plan_queryset[1].start_datetime
            Plans[3]=next_plan_queryset[1].name
        else:
            Plans[2]=""
            Plans[3]=""


        if(len(bio)==0):
            bio="設定されていません"
        return render(request,"calendar_app/account.html",{"User":User,"user_name": user_name,"bio":bio,"Plans":Plans,"friends_len":str(len(friends)),"icon":icon,"user_id":user_id})

class TodoView(LoginRequiredMixin,View):
    def get(self,request):
        user_name = str(request.user)
        now = timezone.now()
        next_todo_queryset = Todo.objects.filter(end_datetime__gte=now, user=str(request.user)).order_by('end_datetime')[:10]
        Todos=[0]*30
        for i in range(10):
            if(i<len(next_todo_queryset)):
                Todos[i*3]=next_todo_queryset[i].name
                Todos[i*3+1]=next_todo_queryset[i].end_datetime
                if(next_todo_queryset[i].complete==0):
                    Todos[i*3+2]="false"
                else:
                    Todos[i*3+2]="true"

            else:
                Todos[i*3]="null"
                Todos[i*3+1]="0"
                Todos[i*3+2]="false"
        return render(request,"calendar_app/todo.html",{"Todos": Todos})

class TodoCreateView(LoginRequiredMixin,View):
    def get(self,request):
        return render(request,"calendar_app/todo_create.html")
    def post(self,request):
        name=request.POST['event-title']
        event_end=request.POST['event-end']+"+0900"
        Todo.objects.create(
            user=str(request.user),
            name=name,
            end_datetime=event_end,
            )
        return redirect("calendar_app:todo_view")

class AccountEditView(LoginRequiredMixin,View):
    def get(self,request):
        User=UserID.objects.get(id=str(request.user))
        User_data=[0]*5
        User_data[0]=User.id
        User_data[1]=User.name
        User_data[2]=User.email
        User_data[3]=User.introduce
        return render(request,"calendar_app/profile_edit.html",{"User_data": User_data})
    def post(self,request):
        id=str(request.user)
        display_name=request.POST['display-name']
        email=request.POST['email']
        bio=request.POST['bio']
        avatar_upload=request.FILES.get('avatar-upload')
        #print("画像:"+str(avatar_upload))
        User = get_object_or_404(UserID, id=id)
        User.name=display_name
        User.email=email
        User.introduce=bio
        User.icon=avatar_upload
        User.save()
        return redirect("calendar_app:account_view")



class FriendView(LoginRequiredMixin,View):
    def get(self,request):
        service = friend.friendService()
        requests=service.get_request_list(str(request.user))
        friends=service.get_friend_list(str(request.user))
        friends_with_icons = []
        requests_with_icons = []
        for a_request in requests:
            icon=UserID.objects.get(id=a_request).icon
            requests_with_icons.append({"id": a_request,"icon": icon})
        for a_friend in friends:
            icon=UserID.objects.get(id=a_friend).icon
            friends_with_icons.append({"id": a_friend,"icon": icon})

        return render(request,"calendar_app/friend.html",{"requests_len":str(len(requests)),"friends_len":str(len(friends)),"requests_with_icons":requests_with_icons,"friends_with_icons":friends_with_icons})
    def post(self,request):
        request_id=request.POST['request-id']
        service = friend.friendService()
        print(str(request.user)+"から"+request_id)
        service.create_request(str(request.user),request_id)
        return redirect("calendar_app:friend_view")


class AcceptRequestView(LoginRequiredMixin,View):
    def get(self,request,id):
        service = friend.friendService()
        service.accept_request(id,str(request.user))
        return redirect("calendar_app:friend_view")

class FriendDeleteView(LoginRequiredMixin,View):
    def get(self,request,id):
        service = friend.friendService()
        service.delete_friend(id,str(request.user))
        return redirect("calendar_app:friend_view")

class CompareView(LoginRequiredMixin,View):
    def get(self,request):
        return render(request,"calendar_app/compare.html")

class FriendCalendarView(LoginRequiredMixin,View):
    def get(self,request,id):
        service = friend.friendService()
        if(not(service.is_friend(str(request.user),id))):
            return redirect("calendar_app:friend_view")
        now = timezone.now()
        next_plan_queryset = Plan.objects.filter(start_datetime__gte=now, user=id, private=0).order_by('start_datetime')[:20]
        before_plan_queryset = Plan.objects.filter(start_datetime__lte=now, user=id, private=0).order_by('-start_datetime')[:20]
        #print(next_plan_queryset[0])
        print(len(before_plan_queryset))
        #events = [[0 for j in range(3)] for i in range(50)]
        event_name=[0 for j in range(50)]
        event_start=[0 for j in range(50)]
        event_end=[0 for j in range(50)]
        event_category = "work"
        for i in range(20):
            if(i<len(next_plan_queryset)):
                event_name[i]=next_plan_queryset[i].name
                event_start[i]=str(next_plan_queryset[i].start_datetime+timedelta(hours=9)).replace(' ','T')[:-6]
                event_end[i]=str(next_plan_queryset[i].end_datetime+timedelta(hours=9)).replace(' ','T')[:-6]
                #print(next_plan_queryset[i].start_datetime)
                #print(event_start[i])
            else:
                event_name[i]="null"
                event_start[i]="2015-12-12T23:00:00"
                event_end[i]="2015-12-12T23:30:00"

        for i in range(20,40):
            if(i<len(before_plan_queryset)+20):
                event_name[i]=before_plan_queryset[i-20].name
                event_start[i]=str(before_plan_queryset[i-20].start_datetime+timedelta(hours=9)).replace(' ','T')[:-6]
                event_end[i]=str(before_plan_queryset[i-20].end_datetime+timedelta(hours=9)).replace(' ','T')[:-6]
                #print(event_name[i])
            else:
                event_name[i]="null"
                event_start[i]="2015-12-12T23:00:00"
                event_end[i]="2015-12-12T23:30:00"

        return render(request,"calendar_app/index.html",{"event_name":event_name,"event_start":event_start,"event_end":event_end,"event_category":event_category})

class PlanDeleteView(LoginRequiredMixin,View,id):
    def get(self,request):
        return render(request,"calendar_app/compare.html")





index=IndexView.as_view()
account_create=AccountCreateView.as_view()
plan_create=PlanCreateView.as_view()
routine_create=RoutineCreateView.as_view()
search_view=SearchView.as_view()
account_view=AccountViewView.as_view()
todo_view=TodoView.as_view()
todo_create_view=TodoCreateView.as_view()
account_edit_view=AccountEditView.as_view()
friend_view=FriendView.as_view()
accept_request=AcceptRequestView.as_view()
friend_delete=FriendDeleteView.as_view()
compare_view=CompareView.as_view()
friend_calendar=FriendCalendarView.as_view()