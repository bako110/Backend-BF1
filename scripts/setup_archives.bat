@echo off
echo ========================================
echo Configuration du systeme Archives
echo ========================================
echo.

echo 1. Creation des archives de test...
python scripts\create_test_archives.py

echo.
echo 2. Test de l'API Archives...
python scripts\test_archives_api.py

echo.
echo ========================================
echo Configuration terminee!
echo ========================================
pause
