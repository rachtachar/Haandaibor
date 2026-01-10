#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# สั่งรวบรวมไฟล์ Static (CSS/JS)
python manage.py collectstatic --no-input

# สั่ง Migrate Database (สร้างตาราง)
python manage.py migrate