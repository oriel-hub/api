from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm
from userprofile.models import UserProfile
 
class ProfileForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        try:
            self.fields['email'].initial = self.instance.user.email
            # self.fields['first_name'].initial = self.instance.user.first_name
            # self.fields['last_name'].initial = self.instance.user.last_name
        except User.DoesNotExist:
            pass

    email = forms.EmailField(label="Primary email", help_text='')

    class Meta:
        model = UserProfile
        exclude = ('user', 'access_guid', 'beacon_guid',)

    def save(self, *args, **kwargs):
        """
        Update the primary email address on the related User object as well.
        """
        user = self.instance.user
        user.email = self.cleaned_data['email']
        user.save()
        profile = super(ProfileForm, self).save(*args, **kwargs)
        # if no GUID created, then make one
        if profile.access_guid in [None, '']:
            profile.generate_access_guid()
        if profile.beacon_guid in [None, '']:
            profile.generate_beacon_guid()
        profile.save()
        return profile
