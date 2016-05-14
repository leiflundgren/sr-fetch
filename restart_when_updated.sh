#!/bin/sh

echo "leifdev restarter started"
touch /etc/uwsgi/apps-available/leifdev.leiflundgren.com.ini

has_changed() {
    r=1
    for f in `find /home/leif/src/py_web -name '*.py' -cnewer /etc/uwsgi/apps-available/leifdev.leiflundgren.com.ini`; do 
        echo `date +'%H:%M:%S: '` $f has changed
        r=0
    done
    return $r
}

while true; do
    sleep 1
    if has_changed; then
        echo 'touching uwsgi'
        touch /etc/uwsgi/apps-available/leifdev.leiflundgren.com.ini
    fi
done
