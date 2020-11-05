#!/bin/sh

web_ip=`./web_ip.sh`

echo $web_ip 

./manage.py.sh "runserver 0.0.0.0:8000"

