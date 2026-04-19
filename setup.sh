#!/bin/bash
echo "=== MediCare HMS Setup ==="
pip install -r requirements.txt
cp .env.example .env
echo "Edit .env with your settings, then run:"
echo "  python manage.py migrate"
echo "  python manage.py createsuperuser"
echo "  python manage.py runserver"
