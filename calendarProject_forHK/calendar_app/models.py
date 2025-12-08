from django.db import models
import uuid

# Create your models here.

class UserID(models.Model):
    id=models.CharField(max_length=30,verbose_name="ユーザー名",primary_key=True)
    password=models.CharField(max_length=100,verbose_name="パスワード",null=True)

    def __str__(self):
        return self.id

class Plan(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,verbose_name="ID")
    user=models.CharField(max_length=30,verbose_name="ユーザーID")
    name=models.CharField(max_length=100,verbose_name="予定名")
    memo=models.TextField(max_length=1000,verbose_name="メモ",null=True)
    private=models.IntegerField(verbose_name="プライバシー設定",choices=[(0,"公開"),(1,"非公開")])
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    updated_time=models.DateTimeField(auto_now=True,verbose_name="更新日時")

    def __str__(self):
        return self.name
    
class Routine(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,verbose_name="ID")
    user=models.CharField(max_length=30,verbose_name="ユーザーID")
    name=models.CharField(max_length=100,verbose_name="予定名")
    day_of_week=models.IntegerField(verbose_name="曜日",choices=[(0,"日曜"),(1,"月曜"),(2,"火曜"),(3,"水曜"),(4,"木曜"),(5,"金曜"),(6,"土曜")])
    private=models.IntegerField(verbose_name="プライバシー設定",choices=[(0,"公開"),(1,"非公開")])
    start_time = models.TimeField()
    end_time = models.TimeField()
    updated_time=models.DateTimeField(auto_now=True,verbose_name="更新日時")

    def __str__(self):
        return self.name
