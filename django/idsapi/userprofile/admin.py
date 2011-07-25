from django.contrib import admin 
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from models import UserProfile 

#class UserProfileAdmin(admin.ModelAdmin): 
#    list_display = ('user_level', 'access_guid', 'beacon_guid') 
#
#admin.site.register(UserProfile, UserProfileAdmin) 

class UserProfileInline(admin.StackedInline): 
    model = UserProfile 
class MyUserAdmin(UserAdmin): 
    inlines = [ 
        UserProfileInline, 
    ] 
admin.site.unregister(User) 
admin.site.register(User, MyUserAdmin) 
