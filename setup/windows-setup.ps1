'''
Author:     Sai Vignesh Golla
LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

Copyright (C) 2024 Sai Vignesh Golla

License:    GNU Affero General Public License
            https://www.gnu.org/licenses/agpl-3.0.en.html
            
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

'''

# PowerShell setup script for Auto Job Applier

Write-Host "Setting up Auto Job Applier..."

# Check Python installation
try {
    $pythonVersion = python --version
    Write-Host "Found Python: $pythonVersion"
} catch {
    Write-Host "Python is not installed or not in PATH"
    Write-Host "Please install Python from https://www.python.org/downloads/"
    Write-Host "Make sure to check 'Add Python to PATH' during installation"
    exit 1
}

# Create virtual environment
Write-Host "Creating virtual environment..."
python -m venv venv
./venv/Scripts/Activate.ps1
    Write-Host "Please install Google Chrome to continue..."
    Write-Host "Hold Ctrl and click on the link below or manually open a browser and search 'Google Chrome Download'."
    Write-Host "https://www.google.com/chrome/"
    Write-Host "After the installation is complete, press Enter to continue."
    Read-Host -Prompt ""
}

Write-Host "Google Chrome is installed."

# Install required Python packages
pip install selenium
pip install undetected-chromedriver

# Get the latest ChromeDriver version
$latestVersionUrl = "https://chromedriver.storage.googleapis.com/LATEST_RELEASE"
$latestVersion = Invoke-WebRequest -Uri $latestVersionUrl -UseBasicParsing | Select-Object -ExpandProperty Content

# Download ChromeDriver
$chromeDriverUrl = "https://chromedriver.storage.googleapis.com/$latestVersion/chromedriver_win32.zip"
$chromeDriverZip = "chromedriver.zip"
$chromeDriverDir = "chromedriver"
Invoke-WebRequest -Uri $chromeDriverUrl -OutFile $chromeDriverZip
Expand-Archive -Path $chromeDriverZip -DestinationPath $chromeDriverDir
Remove-Item -Path $chromeDriverZip

# Set up environment variables
$env:CHROME_DRIVER_PATH = "$($PWD.Path)\$chromeDriverDir\chromedriver.exe"
$env:PATH += ";$($PWD.Path)\$chromeDriverDir"

Write-Host "Setup complete. You can now use the web scraping tool."
Read-Host -Prompt "Press any button to continue..."

