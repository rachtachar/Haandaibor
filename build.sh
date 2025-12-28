#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Install Node.js dependencies (for Tailwind) & Build CSS
# ตรวจสอบว่าไฟล์ package.json อยู่ที่ theme/static_src/
python manage.py tailwind install
python manage.py tailwind build

# 3. Collect Static files
python manage.py collectstatic --no-input

# 4. Migrate Database
python manage.py migrate