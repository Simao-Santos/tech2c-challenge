#!/bin/bash

# Run migrations
python manage.py migrate

# Start server
python manage.py runserver 0.0.0.0:${DJANGO_PORT} --noreload