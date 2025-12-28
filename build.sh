#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Collect Static files
python manage.py collectstatic --no-input

# 3. Migrate Database
python manage.py migrate