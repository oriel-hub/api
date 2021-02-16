#!/bin/bash

source settings.sh

docker-compose exec -T web /bin/bash -x <<EOF
if [ ! -f \$HOME/.django_bashrc ] ; then
    cat > \$HOME/.django_bashrc <<FOO
cd $DJANGO_HOME
source $DJANGO_HOME/.ve/bin/activate
FOO
fi
if [ ! -f \$HOME/.bash_history ] ; then
    cat > \$HOME/.bash_history <<FOO
../../docker/init.sh
./manage.py test
FOO
fi
EOF

docker-compose exec web env TERM=screen bash --rcfile /root/.django_bashrc -i
