from django.conf.urls.defaults import patterns, url
from django.contrib import admin 
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from userprofile.models import UserProfile

import unicodecsv
 
@staff_member_required
def download_view(request):
    "A view to download all instances of this model as a CSV file."
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=users.csv'
    
    writer = unicodecsv.writer(response)
    for user in User.objects.all():
        profile = user.get_profile()
        writer.writerow([
            user.username,
            user.first_name,
            user.last_name,
            user.email,
            user.is_staff,
            user.is_active,
            user.is_superuser,
            user.last_login,
            user.date_joined,
            str(user.groups.all()),
            profile.user_level,
            profile.organisation,
            profile.organisation_url,
            profile.organisation_address1,
            profile.organisation_address2,
            profile.organisation_address3,
            profile.city,
            profile.country,
            profile.zip_postal_code,
            profile.organisation_type,
            profile.api_usage_type,
            profile.cms_technology_platform,
            profile.heard_about,
            profile.website_using_api,
            profile.commercial,
            profile.agree_to_licensing,
            ])
    return response

# class UserProfileAdmin(admin.ModelAdmin):
    # list_display = ('user_level', 'access_guid', 'beacon_guid') 
    
# admin.site.register(UserProfile, UserProfileAdmin) 

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    
class MyUserAdmin(UserAdmin):
    inlines = [
        UserProfileInline,
    ]

    def get_urls(self):
        urls = super(MyUserAdmin, self).get_urls()

        urls = patterns('',
            url(r'^download/$', download_view, name='user_list_download'),
        ) + urls
        
        return urls
        
admin.site.unregister(User) 
admin.site.register(User, MyUserAdmin) 
