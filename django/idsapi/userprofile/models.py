from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import signals
from django_countries import CountryField

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

    # things the user will edit in their profile
    name = models.CharField(max_length=50)
    organisation = models.CharField(max_length=100, blank=True)
    organisation_url = models.URLField("Organisation Website", blank=True)
    organisation_address1 = models.CharField("Organisation address (line 1)", max_length=100, blank=True)
    organisation_address2 = models.CharField("Organisation address (line 2)", max_length=100, blank=True)
    organisation_address3 = models.CharField("Organisation address (line 3)", max_length=100, blank=True)
    city = models.CharField(max_length=50, blank=True)
    country = CountryField(blank=True)
    zip_postal_code = models.CharField("ZIP/Postal Code", max_length=20, blank=True)
    ORGANISATION_TYPE_CHOICES = (
            (u'Bilateral Aid Agency',          u'Bilateral Aid Agency'),
            (u'Multilateral Aid Agency',       u'Multilateral Aid Agency'),
            (u'International NGO or CSO',      u'International NGO or CSO'),
            (u'National / Local NGO or CSO',   u'National / Local NGO or CSO'),
            (u'National / Local Government',   u'National / Local Government'),
            (u'Political Party',               u'Political Party'),
            (u'Academic',                      u'Academic'),
            (u'School / college',              u'School / college'),
            (u'Library / Information Service', u'Library / Information Service'),
            (u'Commercial / Business',         u'Commercial / Business'),
            (u'Health Centre / Hospital',      u'Health Centre / Hospital'),
            (u'Media',                         u'Media'),
            (u'Network',                       u'Network'),
            (u'No affiliation',                u'No affiliation'),
            (u'Other (please specify)',        u'Other (please specify)'),
            )
    organisation_type = models.CharField(max_length=50, blank=True, choices=ORGANISATION_TYPE_CHOICES)
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
