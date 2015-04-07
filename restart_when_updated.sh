#!/bin/sh

while true; do
    for f in `find /home/leif/src/sr -name '*.py' -cnewer /etc/uwsgi/apps-available/sr.leiflundgren.com.ini`; do 
        sleep 1
        echo $f has changed
        touch /etc/uwsgi/apps-available/sr.leiflundgren.com.ini
    done
    sleep 1
done