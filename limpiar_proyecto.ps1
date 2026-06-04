# SCRIPT DE LIMPIEZA AUTOMATICO
Write-Host "Limpiando proyecto..." -ForegroundColor Yellow

# Eliminar backups
Remove-Item -Path "app_backup*.py" -Force -ErrorAction SilentlyContinue
Write-Host "✅ Eliminados app_backup*.py" -ForegroundColor Green

# Eliminar temporales
Remove-Item -Path "temp_func.txt" -Force -ErrorAction SilentlyContinue
Write-Host "✅ Eliminado temp_func.txt" -ForegroundColor Green

# Eliminar __pycache__
Get-ChildItem -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "✅ Eliminadas carpetas __pycache__" -ForegroundColor Green

# Eliminar archivos .pyc
Get-ChildItem -Recurse -Filter "*.pyc" | Remove-Item -Force -ErrorAction SilentlyContinue
Write-Host "✅ Eliminados archivos .pyc" -ForegroundColor Green

Write-Host ""
Write-Host "✅ Limpieza completada!" -ForegroundColor Green
