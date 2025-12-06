from django.urls import path
from . import views
app_name="calendar_app"

urlpatterns=[
  path("",views.index , name="index"),
  path("account/create",views.account_create , name="account_create"),
] 