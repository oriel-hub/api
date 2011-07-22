import uuid
from django.db import models
from django import forms
from django.forms import ModelForm
from models import UserProfile
 
class ProfileForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        try:
            self.fields['email'].initial = self.instance.user.email
            # self.fields['first_name'].initial = self.instance.user.first_name
            # self.fields['last_name'].initial = self.instance.user.last_name
        except User.DoesNotExist:
            pass

    email = forms.EmailField(label="Primary email",help_text='')

    class Meta:
        model = UserProfile
        exclude = ('user', 'access_guid', 'beacon_guid',)

    def save(self, *args, **kwargs):
        """
        Update the primary email address on the related User object as well.
        """
        u = self.instance.user
        u.email = self.cleaned_data['email']
        u.save()
        profile = super(ProfileForm, self).save(*args,**kwargs)
        # if no GUID created, then make one
        if profile.access_guid in [None, '']:
            profile.access_guid = str(uuid.uuid4())
        if profile.beacon_guid in [None, '']:
            profile.beacon_guid = str(uuid.uuid4())
        profile.save()
        return profile
