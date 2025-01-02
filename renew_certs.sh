#!/bin/bash

# Pull the latest Certbot image
docker pull certbot/certbot

# Stop Nginx container
docker-compose stop nginx

# Renew certificates
docker run -it --rm \
  -v $(pwd)/nginx/certs:/etc/letsencrypt \
  -v $(pwd)/nginx/www:/var/www/certbot \
  certbot/certbot renew --webroot --webroot-path=/var/www/certbot