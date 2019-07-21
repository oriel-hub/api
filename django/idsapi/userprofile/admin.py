from django.conf.urls  import url
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from userprofile.models import UserProfile

import unicodecsv

CSV_COL_NAMES = [
            'Username',
            'First name',
            'Last name',
            'Email',
            'Is staff',
            'Is active',
            'Is superuser',
            'Last login',
            'Date joined',
            'User level',
            'Organisation',
            'Organisation url',
            'Organisation address line 1',
            'Organisation address line 2',
            'Organisation address line 3',
            'City',
            'Country',
            'Zip/postal code',
            'Organisation type',
            'API usage type',
            'CMS technology platform',
            'Heard about',
            'Website using API',
            'Commercial',
            'Agree to licensing',
            'Access GUID',
            'Beacon GUID',
        ]

@staff_member_required
def download_view(request):
    "A view to download all instances of this model as a CSV file."
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=users.csv'

    writer = unicodecsv.writer(response)
    writer.writerow(CSV_COL_NAMES)
    for user in User.objects.all():
        profile = user.userprofile
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
            profile.access_guid,
            profile.beacon_guid,
            ])
    return response

# class UserProfileAdmin(admin.ModelAdmin):
    # list_display = ('user_level', 'access_guid', 'beacon_guid')

# admin.site.register(UserProfile, UserProfileAdmin)

class UserProfileInline(admin.StackedInline):
    model = UserProfile

class MyUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ('user_level',)

    def user_level(self, obj):
        try:
            return obj.userprofile.user_level
        except (obj.DoesNotExist, ObjectDoesNotExist):
            return "not set yet"

    inlines = [
        UserProfileInline,
    ]

    def get_urls(self):
        urls = super(MyUserAdmin, self).get_urls()

        urls = ['',
            url(r'^download/$', download_view, name='user_list_download'),
        ] + urls

        return urls

admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)
