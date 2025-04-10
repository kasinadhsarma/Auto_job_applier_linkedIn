# LinkedIn Auto Job Applier Setup Script for Windows
# Run this script in PowerShell with appropriate execution policy

# Output colors
$RED = [System.ConsoleColor]::Red
$GREEN = [System.ConsoleColor]::Green
$YELLOW = [System.ConsoleColor]::Yellow

Write-Host "Setting up LinkedIn Auto Job Applier..." -ForegroundColor $GREEN

# Check Python version
try {
    $pythonVersion = python -c "import sys; print('.'.join(map(str, sys.version_info[:2])))"
    if ([version]$pythonVersion -lt [version]"3.8") {
        Write-Host "Error: Python 3.8 or higher is required." -ForegroundColor $RED
        Write-Host "Current version: $pythonVersion"
        exit 1
    }
} catch {
    Write-Host "Error: Python is not installed or not in PATH." -ForegroundColor $RED
    exit 1
}

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor $YELLOW
try {
    python -m venv venv
    if (-not $?) {
        Write-Host "Failed to create virtual environment." -ForegroundColor $RED
        exit 1
    }
} catch {
    Write-Host "Failed to create virtual environment: $_" -ForegroundColor $RED
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor $YELLOW
try {
    .\venv\Scripts\Activate.ps1
} catch {
    Write-Host "Failed to activate virtual environment: $_" -ForegroundColor $RED
    exit 1
}

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor $YELLOW
python -m pip install --upgrade pip

# Install requirements
Write-Host "Installing requirements..." -ForegroundColor $YELLOW
try {
    pip install -r requirements.txt
    if (-not $?) {
        Write-Host "Failed to install requirements." -ForegroundColor $RED
        exit 1
    }
} catch {
    Write-Host "Failed to install requirements: $_" -ForegroundColor $RED
    exit 1
}

# Create configuration files
Write-Host "Setting up configuration files..." -ForegroundColor $YELLOW
Get-ChildItem -Path "config" -Filter "*.example" | ForEach-Object {
    $target = $_.FullName -replace '\.example$', ''
    if (-not (Test-Path $target)) {
        Copy-Item $_.FullName $target
        Write-Host "Created $target"
    } else {
        Write-Host "Config file $target already exists, skipping..."
    }
}

# Create data directories
Write-Host "Creating data directories..." -ForegroundColor $YELLOW
@(
    "data\logs\screenshots",
    "data\resumes",
    "data\history"
) | ForEach-Object {
    New-Item -Path $_ -ItemType Directory -Force | Out-Null
}

@(
    "data\resumes\.gitkeep",
    "data\logs\.gitkeep",
    "data\history\.gitkeep"
) | ForEach-Object {
    New-Item -Path $_ -ItemType File -Force | Out-Null
}

# Set up Git hooks if .git directory exists
if (Test-Path ".git") {
    Write-Host "Setting up Git hooks..." -ForegroundColor $YELLOW
    $hookContent = @"
#!/bin/sh
if git diff --cached --name-only | grep -q "config/secrets.py"; then
    echo "Error: Attempted to commit secrets.py file"
    exit 1
fi
"@
    $hookContent | Out-File -FilePath ".git\hooks\pre-commit" -Encoding ASCII
}

# Final instructions
Write-Host "`nSetup completed successfully!" -ForegroundColor $GREEN
Write-Host "`nNext steps:" -ForegroundColor $YELLOW
Write-Host "1. Copy your resume to data\resumes\" -ForegroundColor $YELLOW
Write-Host "2. Update configuration files in config\" -ForegroundColor $YELLOW
Write-Host "3. Create config\secrets.py with your LinkedIn credentials" -ForegroundColor $YELLOW

Write-Host "`nTo activate the virtual environment, run:" -ForegroundColor $GREEN
Write-Host ".\venv\Scripts\Activate.ps1"

Write-Host "`nTo start the application, run:" -ForegroundColor $GREEN
Write-Host "python main.py"
