# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import userprofile.models
from django.conf import settings
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('access_guid', models.CharField(max_length=36)),
                ('beacon_guid', models.CharField(max_length=36)),
                ('user_level', models.CharField(max_length=50, verbose_name=b'User Level', choices=[(b'General User', b'General User'), (b'Offline Application User', b'Offline Application User'), (b'Partner', b'Partner'), (b'Unlimited', b'Unlimited')])),
                ('organisation', models.CharField(max_length=100, blank=True)),
                ('organisation_url', models.URLField(verbose_name=b'Organisation Website', blank=True)),
                ('organisation_address1', models.CharField(max_length=100, verbose_name=b'Organisation address (line 1)', blank=True)),
                ('organisation_address2', models.CharField(max_length=100, verbose_name=b'Organisation address (line 2)', blank=True)),
                ('organisation_address3', models.CharField(max_length=100, verbose_name=b'Organisation address (line 3)', blank=True)),
                ('city', models.CharField(max_length=50, blank=True)),
                ('country', django_countries.fields.CountryField(blank=True, max_length=2)),
                ('zip_postal_code', models.CharField(max_length=20, verbose_name=b'ZIP/Postal Code', blank=True)),
                ('organisation_type', models.CharField(blank=True, max_length=50, choices=[('Bilateral Aid Agency', 'Bilateral Aid Agency'), ('Multilateral Aid Agency', 'Multilateral Aid Agency'), ('International NGO or CSO', 'International NGO or CSO'), ('National / Local NGO or CSO', 'National / Local NGO or CSO'), ('National / Local Government', 'National / Local Government'), ('Political Party', 'Political Party'), ('Academic', 'Academic'), ('School / college', 'School / college'), ('Library / Information Service', 'Library / Information Service'), ('Commercial / Business', 'Commercial / Business'), ('Health Centre / Hospital', 'Health Centre / Hospital'), ('Media', 'Media'), ('Network', 'Network'), ('No affiliation', 'No affiliation'), ('Other (please specify', 'Other (please specify')])),
                ('organisation_type_text', models.CharField(max_length=50, verbose_name=b'Organisation Type (if other selected)', blank=True)),
                ('api_usage_type', models.CharField(max_length=50, verbose_name=b'API usage type', blank=True)),
                ('cms_technology_platform', models.CharField(max_length=50, verbose_name=b'CMS/Technology platform', blank=True)),
                ('heard_about', models.CharField(max_length=250, verbose_name=b'How did you hear about us?', blank=True)),
                ('website_using_api', models.URLField(verbose_name=b'Website that will use the API')),
                ('commercial', models.CharField(max_length=50, verbose_name=b'Usage', choices=[('Commercial', 'Commercial'), ('Non-Commercial', 'Non-Commercial')])),
                ('agree_to_licensing', models.BooleanField(default=False, verbose_name='I have read and agree to the Terms and Conditions', validators=[userprofile.models.validate_agreed_to_license_terms])),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
        ),
    ]
