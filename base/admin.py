from django.contrib import admin
from .models import User,Committees,Department,Folder,File,UserList


admin.site.register(Committees)
admin.site.register(Department)
admin.site.register(User)
admin.site.register(UserList)
admin.site.register(Folder)
admin.site.register(File)

# Register your models here.
