#!/bin/bash
set -e

echo "=========================================================="
echo " Starting Setup for certificate.natdemy.com on Ubuntu EC2 "
echo "=========================================================="

APP_DIR="/var/www/certificate.natdemy.com"

# 1. Update system packages and ensure python3-venv and nginx are installed
sudo apt update
sudo apt install -y python3-pip python3-venv python3-dev nginx certbot python3-certbot-nginx

# 2. Setup Virtual Environment
cd $APP_DIR
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# 3. Install Python dependencies
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

# 4. Run Migrations & Collect Static Files
./venv/bin/python manage.py migrate
./venv/bin/python manage.py collectstatic --noinput

# 5. Create default admin if not existing
./venv/bin/python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'certificate_project.settings')
django.setup()
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@natdemy.com', 'admin123')
    print('Superuser admin created: admin / admin123')
"

# 6. Ensure permissions for www-data and ubuntu
sudo chown -R ubuntu:www-data $APP_DIR
sudo chmod -R 775 $APP_DIR
sudo chmod -R 775 $APP_DIR/db.sqlite3 2>/dev/null || true

# 7. Configure Systemd Service
sudo cp $APP_DIR/deploy/certificate.service /etc/systemd/system/certificate.service
sudo systemctl daemon-reload
sudo systemctl start certificate
sudo systemctl enable certificate

# 8. Configure Nginx Virtual Host
sudo cp $APP_DIR/deploy/nginx_certificate.conf /etc/nginx/sites-available/certificate.natdemy.com
sudo ln -sf /etc/nginx/sites-available/certificate.natdemy.com /etc/nginx/sites-enabled/

# 9. Test and reload Nginx
sudo nginx -t
sudo systemctl reload nginx

echo "=========================================================="
echo " Setup complete! Next step: SSL with Certbot:             "
echo " sudo certbot --nginx -d certificate.natdemy.com          "
echo "=========================================================="
