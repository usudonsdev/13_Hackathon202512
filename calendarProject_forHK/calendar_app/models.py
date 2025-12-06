from django.db import models

# Create your models here.

class UserID(models.Model):
    id=models.CharField(max_length=30,verbose_name="ユーザー名",primary_key=True)
    password=models.CharField(max_length=100,verbose_name="パスワード",null=True)

    def __str__(self):
        return self.id
