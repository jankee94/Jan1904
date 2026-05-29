@echo off
git add .
git commit -m "Auto commit %date% %time%"
git push
echo.
echo ¡Listo! Cambios subidos a GitHub
pause