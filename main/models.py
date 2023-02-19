import os
from django.db import models
from django.contrib.auth.models import User

def get_upload_to(instance, filename):
    folder_name = os.path.join('uploads', instance.file_code)
    return os.path.join(folder_name, filename)

class UserData(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class FilePost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    file_code = models.CharField(max_length=10, unique=True, null=True)
    file_hash = models.CharField(max_length=100, null=True)
    file = models.FileField(upload_to=get_upload_to)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name