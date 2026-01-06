#!/usr/bin/env bash


# Run daily on crontab e.g.
#  Your cron job will be run at: (5 times displayed)
#
#    2021-11-08 11:10:00 UTC
#    2021-11-09 11:10:00 UTC
#    2021-11-10 11:10:00 UTC
#    2021-11-11 11:10:00 UTC
#    2021-11-12 11:10:00 UTC
#    ...etc

#25 11 * * * /bin/bash /home/web/QGIS-Changelog-Website/deployment/scripts/renew_ssl.sh > /tmp/ssl-renewal-logs.txt

# Set variables for cleaner commands
DEPLOYMENT_DIR="/home/web/QGIS-Changelog-Website/deployment"
COMPOSE_FILES="-f ${DEPLOYMENT_DIR}/docker-compose.yml -f ${DEPLOYMENT_DIR}/docker-compose.override.yml"

# Renew SSL certificates
docker compose ${COMPOSE_FILES} run certbot renew

# Hot reload the web service to apply new certificates
docker compose ${COMPOSE_FILES} kill -s SIGHUP web
