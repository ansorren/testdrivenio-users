#!/bin/sh

while !nc -z users-db 5432; do
  sleep 1
done

echo "postgres started"
python manage.py run -h 0.0.0.0
