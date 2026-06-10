# run.ps1
# Script para iniciar la aplicación

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 SG-SST PHVA - PLATAFORMA EMPRESARIAL" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Verificar Python
Write-Host "📌 Verificando entorno..." -ForegroundColor Yellow
python --version

# Instalar dependencias si es necesario
Write-Host "`n📦 Instalando dependencias..." -ForegroundColor Yellow
pip install -r requirements.txt

# Verificar archivo .env
if (-not (Test-Path ".env")) {
    Write-Host "⚠️ No existe archivo .env. Copia .env.example y configura tus credenciales" -ForegroundColor Red
}

# Ejecutar la app
Write-Host "`n🚀 Iniciando aplicación..." -ForegroundColor Green
streamlit run app/main.py
