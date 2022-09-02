#!/usr/bin/env python

import os
import secrets
import string

DEPLOY_DIR = os.path.dirname(os.path.realpath(__file__))
SETTINGS_DIR = os.path.join(DEPLOY_DIR, "..", "django", "idsapi")
PRIVATE_SETTINGS_FILE = os.path.join(SETTINGS_DIR, "private_settings.py")

characters = string.ascii_letters + string.digits + string.punctuation
with open(PRIVATE_SETTINGS_FILE, "w") as f:
    secret_key = "".join([secrets.choice(characters) for i in range(50)])
    db_password = "".join([secrets.choice(characters) for i in range(12)])

    f.write(f"SECRET_KEY = '{secret_key}'\n")
    f.write(f"DB_PASSWORD = '{db_password}'\n")
