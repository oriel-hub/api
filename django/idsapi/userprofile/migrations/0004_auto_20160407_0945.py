# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import userprofile.models


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0003_userprofile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='agree_to_licensing',
            field=models.BooleanField(default=False, verbose_name='I have read and agree to the Terms and Conditions', validators=[userprofile.models.validate_agreed_to_license_terms]),
        ),
    ]
