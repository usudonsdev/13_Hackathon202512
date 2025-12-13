from django.db import models
import uuid

# Create your models here.

class UserID(models.Model):
    id=models.CharField(max_length=30,verbose_name="ユーザー名",primary_key=True)
    password=models.CharField(max_length=100,verbose_name="パスワード",null=True)
    name=models.CharField(max_length=100,verbose_name="名前",null=True,blank=True)
    icon=models.ImageField(upload_to="calendar_app/picture/",verbose_name="アイコン",null=True,blank=True)
    email=models.CharField(max_length=100,verbose_name="メールアドレス",null=True,blank=True)
    introduce=models.TextField(max_length=1000,verbose_name="自己紹介",null=True,blank=True)


    def __str__(self):
        return self.id

class Plan(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,verbose_name="ID")
    user=models.CharField(max_length=30,verbose_name="ユーザーID")
    name=models.CharField(max_length=100,verbose_name="予定名")
    memo=models.TextField(max_length=1000,verbose_name="メモ",null=True,blank=True)
    private=models.IntegerField(verbose_name="プライバシー設定",choices=[(0,"公開"),(1,"非公開")])
    category=models.CharField(max_length=30,verbose_name="色設定",default="meeting",choices=[("meeting","青"),("private","赤"),("personal","緑"),("work","オレンジ")])
    start_datetime = models.DateTimeField(verbose_name="期間の始まり")
    end_datetime = models.DateTimeField(verbose_name="期間の終わり")
    updated_time=models.DateTimeField(auto_now=True,verbose_name="更新日時")

    def __str__(self):
        return self.name
    
class Routine(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,verbose_name="ID")
    user=models.CharField(max_length=30,verbose_name="ユーザーID")
    name=models.CharField(max_length=100,verbose_name="予定名")
    day_of_week=models.IntegerField(verbose_name="曜日",choices=[(0,"日曜"),(1,"月曜"),(2,"火曜"),(3,"水曜"),(4,"木曜"),(5,"金曜"),(6,"土曜")])
    private=models.IntegerField(verbose_name="プライバシー設定",choices=[(0,"公開"),(1,"非公開")])
    start_time = models.TimeField(verbose_name="期間の始まり")
    end_time = models.TimeField(verbose_name="期間の終わり")
    updated_time=models.DateTimeField(auto_now=True,verbose_name="更新日時")

    def __str__(self):
        return self.name

class friend(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,verbose_name="ID")
    user1=models.CharField(max_length=30,verbose_name="ユーザー1")
    user2=models.CharField(max_length=30,verbose_name="ユーザー2")
    accept=models.IntegerField(verbose_name="承認状態") #0=申請中, 1=承認済み

    def __str__(self):
        return self.user2

class Todo(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,verbose_name="ID")
    user=models.CharField(max_length=30,verbose_name="ユーザーID")
    name=models.CharField(max_length=101,verbose_name="予定名")
    end_datetime = models.DateTimeField(verbose_name="締め切り")
    updated_time=models.DateTimeField(auto_now=True,verbose_name="更新日時")
    complete=models.IntegerField(default=0,verbose_name="完了")


    def __str__(self):
        return self.name