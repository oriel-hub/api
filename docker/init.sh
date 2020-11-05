#!/bin/bash

python_install () { 
    ../../deploy/bootstrap.py --dev -rf
}

config () {
    ../../deploy/tasks.py clean_db
    ../../deploy/tasks.py update_db:syncdb=False
    ../../deploy/tasks.py deploy:dev
    # ../../deploy/tasks.py restore_db:/var/django/inaspauthoraid/deploy/db_dump.sql
    ./manage.py migrate 
    ./manage.py check
    # Run test setup with create-db so it's created (subsequent test runs will
    # reuse the db for performance - but note this needs recreating if
    # migrations are run)
    ./manage.py test --setup-only --create-db --migrations
}


echo "Python install"
python_install

echo "Config"
config
