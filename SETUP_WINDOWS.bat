@echo off
REM MarketPlace setup for Windows
REM Run this after extracting the zip and installing Python 3.10+

echo Installing required packages...
pip install django djangorestframework django-filter

echo Starting server...
echo.
echo Storefront: http://127.0.0.1:8000/
echo API: http://127.0.0.1:8000/api/products/
echo.
python manage.py runserver
