#!/bin/sh

echo "leifdev restarter started"
touch /etc/uwsgi/apps-available/leifdev.leiflundgren.com.ini

while true; do
    for f in `find /home/leif/src/py_web -name '*.py' -cnewer /etc/uwsgi/apps-available/leifdev.leiflundgren.com.ini`; do 
        sleep 1
        echo `date +'%H:%M:%S: '` $f has changed
        touch /etc/uwsgi/apps-available/leifdev.leiflundgren.com.ini
    done
    sleep 1
done
