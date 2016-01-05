from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm

from .models import UserProfile


class ProfileForm(ModelForm):

    first_name = forms.CharField(label="First name", help_text='')
    last_name = forms.CharField(label="Last name", help_text='')
    email = forms.EmailField(label="Primary email", help_text='')

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        # do it this way for ordering
        try:
            self.fields['email'].initial = self.instance.user.email
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
        except User.DoesNotExist:
            pass

    class Meta:
        model = UserProfile
        fields = ('first_name', 'last_name', 'email')
        exclude = ('user', 'access_guid', 'beacon_guid', 'user_level', )

    def save(self, *args, **kwargs):
        """
        Update the primary email address on the related User object as well.
        """
        user = self.instance.user
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        profile = super(ProfileForm, self).save(*args, **kwargs)
        # if no GUID created, then make one
        profile.ensure_hidden_fields_set()
        profile.save()
        return profile
