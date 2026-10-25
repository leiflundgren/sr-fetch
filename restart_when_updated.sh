#!/bin/sh

echo "leifdev restarter started"
sudo systemctl restart gunicorn-sr-fetch.service
