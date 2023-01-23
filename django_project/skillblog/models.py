from django.db import models
import jsonfield
from django.utils import timezone
from django.contrib.auth.models import User
# Create your models here.

class Posts(models.Model):
    title = models.CharField(max_length= 100)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

# create another model Employee with below columns
# name, employee_id, email, DOB, Phone, created_at, updated_at, Designation

class Resume(models.Model):
    # id, file_path, file_name, result_json,employee_id,created_at,updated_at  
    # join Resume and Employee Table
    # create a sample page to upload
    # how to upload file and store it in some path and store file path in db
    resume = jsonfield.JSONField() # 




