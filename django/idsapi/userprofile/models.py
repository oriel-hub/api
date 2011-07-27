import uuid

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import signals
from django_countries import CountryField

from django.conf import settings

from userprofile.signals import create_profile

def validate_agreed_to_license_terms(value):
    if value != True:
        raise ValidationError(u'You must agree to the terms to continue')
 
# When model instance is saved, trigger creation of corresponding profile
signals.post_save.connect(create_profile, sender=User)

class UserProfile(models.Model):
    # so we can get it with user.get_profile()
    user = models.OneToOneField(User)

    # the access guid is to authenticate against the API
    access_guid = models.CharField(max_length=36)
    # the beacon guid is an argument to the beacon for usage tracking
    beacon_guid = models.CharField(max_length=36)

    # user level
    user_levels = sorted(settings.USER_LEVEL_INFO.keys())
    choices = []
    for level in user_levels:
        choices.append((level, level))
    USER_LEVEL_CHOICES = tuple(choices)
    user_level = models.CharField("User Level", max_length=50, choices=USER_LEVEL_CHOICES)

    # things the user will edit in their profile
    organisation = models.CharField(max_length=100, blank=True)
    organisation_url = models.URLField("Organisation Website", blank=True)
    organisation_address1 = models.CharField("Organisation address (line 1)", max_length=100, blank=True)
    organisation_address2 = models.CharField("Organisation address (line 2)", max_length=100, blank=True)
    organisation_address3 = models.CharField("Organisation address (line 3)", max_length=100, blank=True)
    city = models.CharField(max_length=50, blank=True)
    country = CountryField(blank=True)
    zip_postal_code = models.CharField("ZIP/Postal Code", max_length=20, blank=True)

    # organisation types - from settings
    choices = []
    for organisation_type in settings.ORGANISATION_TYPES:
        choices.append((organisation_type, organisation_type))
    ORGANISATION_TYPE_CHOICES = tuple(choices)
    organisation_type = models.CharField(max_length=50, blank=True, choices=ORGANISATION_TYPE_CHOICES)
    organisation_type_text = models.CharField("Organisation Type (if other selected)", max_length=50, blank=True)

    api_usage_type = models.CharField("API usage type", max_length=50, blank=True)
    cms_technology_platform = models.CharField("CMS/Technology platform", max_length=50, blank=True)
    heard_about = models.CharField("How did you hear about us?", max_length=250, blank=True)
    website_using_api = models.URLField("Website that will use the API")
    COMMERCIAL_CHOICES = (
            (u'Commercial', u'Commercial'),
            (u'Non-Commercial', u'Non-Commercial'),
            )
    commercial = models.CharField("Usage", max_length=50, choices=COMMERCIAL_CHOICES)
    agree_to_licensing = models.BooleanField(
            u'I have read and agree to the Terms and Conditions',
            validators=[validate_agreed_to_license_terms])

    def ensure_hidden_fields_set(self):
        if self.access_guid in [None, '']:
            self.access_guid = str(uuid.uuid4())
        if self.beacon_guid in [None, '']:
            self.beacon_guid = str(uuid.uuid4())
        if self.user_level in [None, '']:
            self.user_level = u'General User'

