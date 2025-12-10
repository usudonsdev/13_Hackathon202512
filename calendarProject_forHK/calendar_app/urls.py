from django.urls import path
from . import views
app_name="calendar_app"

urlpatterns=[
  path("",views.index , name="index"),
  path("account/create",views.account_create , name="account_create"),
  path("plan/create",views.plan_create , name="plan_create"),
  path("routine/create",views.routine_create , name="routine_create"),
  path("search/view",views.search_view , name="search_view"),
  path("account/view",views.account_view , name="account_view"),
  path("google-calendar/auth/", views.google_calendar_auth_start, name="google_calendar_auth_start"),
  path("oauth2callback/", views.google_calendar_auth_callback, name="google_calendar_auth_callback"),
  

] 