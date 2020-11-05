#!/bin/sh

. settings.sh

docker-compose exec web /bin/bash -c "env LC_ALL=en_GB.UTF-8 LANG=en_GB.UTF-8 LANGUAGE=en_GB.UTF-8 $PROJECT_ROOT/deploy/tasks.py $*"
