#!/bin/bash

echo "running shortener server"

gunicorn wsgi:app --bind 0.0.0.0:8000
