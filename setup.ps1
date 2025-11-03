# PowerShell setup script for Psychiatric Patient Record System
Write-Host "🧠 Setting up Psychiatric Patient Record System..." -ForegroundColor Cyan

# Check Python version
Write-Host "`n📌 Checking Python version..." -ForegroundColor Yellow
python --version

# Create virtual environment
Write-Host "`n📦 Creating virtual environment..." -ForegroundColor Yellow
python -m venv .venv

# Activate virtual environment
Write-Host "`n🔧 Activating virtual environment..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "`n⬆️  Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install dependencies
Write-Host "`n📥 Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Create .env file if it doesn't exist
if (-not (Test-Path .env)) {
    Write-Host "`n📝 Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "⚠️  Please edit .env and add your API keys!" -ForegroundColor Red
}

# Create patients directory
Write-Host "`n📁 Creating patients directory..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "backend\patients" | Out-Null

Write-Host "`n✅ Setup complete!" -ForegroundColor Green
Write-Host "`n📚 Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit .env file and add your API keys"
Write-Host "2. Read CLAUDE.md for development instructions"
Write-Host "3. Run: claude code"
Write-Host ""
