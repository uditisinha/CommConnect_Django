from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
import os
from django.conf import settings
from django.db.models.signals import pre_delete
from django.dispatch import receiver
import shutil

class Department(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class User(AbstractUser):
    avatar = models.ImageField(null = True, upload_to = "images/", blank = True)
    honorific = models.CharField(max_length = 200, null = True, blank = True)
    pname = models.CharField(max_length = 200, null = True)
    email = models.EmailField(unique = True, null = True)
    position = models.CharField(max_length = 200, null = True)
    number = models.BigIntegerField(null = True)
    department = models.ForeignKey(Department,on_delete=models.SET_NULL,null=True)
    is_verified = models.BooleanField(default = False)
    auth_token = models.CharField(max_length = 200)
    password_token = models.CharField(max_length = 200)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['pname', 'username'] 
    

class UserList(models.Model):
    email = models.EmailField(unique = True, max_length = 200)

    def __str__(self):
        return self.email

class Committees(models.Model):
    
    name = models.CharField(max_length = 200)
    description = models.TextField()
    goal = models.TextField()
    objective = models.TextField()
    level = models.CharField(max_length = 200)
    updated = models.DateTimeField(auto_now = True)
    created = models.DateTimeField(auto_now_add = True)
    convener = models.ForeignKey(User, on_delete = models.SET_NULL, null = True,blank=True)
    members = models.ManyToManyField(User,related_name='members',null=True,blank=True)
    staff = models.ManyToManyField(User,related_name='staff',null=True,blank=True)

    def __str__(self):
        return self.name


class Folder(models.Model):
    name = models.CharField(max_length=10000)
    parent_directory = models.CharField(unique=True,max_length=10000,default=os.path.join(settings.MEDIA_ROOT, "files/"))
    def __str__(self):
        return self.name
    

@receiver(pre_delete,sender=Committees)
def delete_committee_folder(sender,instance,**kwargs):
    folder_name = instance.name
    path = str(settings.MEDIA_ROOT) +'\\files/'+f'{folder_name}/'

@receiver(pre_delete, sender=Folder)
def delete_subfolders(sender, instance, **kwargs):
    # Temporarily disconnect the signal to avoid recursion
    pre_delete.disconnect(delete_subfolders, sender=Folder)
    try:
        # Delete subfolders in bulk
        subfiles = File.objects.filter(directory__startswith=instance.parent_directory)
        subfolders = Folder.objects.filter(parent_directory__startswith=instance.parent_directory)
        subfolders.delete()
        subfiles.delete()
        try:
            shutil.rmtree(instance.parent_directory)
        except OSError as e:
            print(f"Error deleting directory: {e}")
    finally:
        # Reconnect the signal after the deletion is done
        pre_delete.connect(delete_subfolders, sender=Folder)

def generate_upload_path(instance,name):
    directory = instance.directory
    return f'{directory}{name}'

class File(models.Model):
    def __str__(self):
        return os.path.basename(self.file.name)
    
    name = models.CharField(max_length=500,null=False)
    file = models.FileField(max_length=20000,upload_to='cat/')
    keywords = models.TextField(max_length=1000,null=True,blank=True)
    directory = models.CharField(max_length=10000)
    committee = models.ForeignKey(Committees,on_delete=models.CASCADE,null=True,blank=True)

@receiver(pre_delete,sender=File)
def delete_files(sender,instance,**kwargs):
    try:
        # Delete the file from the file system
        path =instance.file.path
        os.remove(path)
        print(f"File '{path}' deleted successfully.")
    except OSError as e:
        print(f"Error deleting file: {e}")