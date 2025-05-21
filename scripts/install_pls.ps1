#
# PlainSpeak PLS Alias Installer for Windows
#
# This PowerShell script sets up the 'pls' command alias for PlainSpeak,
# creating a more conversational interface for natural language command translation.
#

# Stop on errors
$ErrorActionPreference = "Stop"

Write-Host "Installing 'pls' alias for PlainSpeak..."

# Get the script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$UserBin = Join-Path $env:USERPROFILE "bin"

# Create user bin directory if it doesn't exist
if (!(Test-Path $UserBin)) {
    Write-Host "Creating $UserBin directory..."
    New-Item -ItemType Directory -Path $UserBin -Force | Out-Null
}

# Get the path to the pls script
$PlsScript = Join-Path $ScriptDir "pls"

if (Test-Path $PlsScript) {
    # Copy the pls script to the user's bin directory
    Write-Host "Installing pls script to $UserBin\pls.ps1..."
    Copy-Item $PlsScript -Destination "$UserBin\pls.ps1" -Force

    # Create a batch file wrapper for easier execution
    @"
@echo off
powershell -ExecutionPolicy Bypass -File "%USERPROFILE%\bin\pls.ps1" %*
"@ | Out-File -FilePath "$UserBin\pls.bat" -Encoding ascii -Force
} else {
    # If script is missing, create a batch file that calls plainspeak
    $PlainSpeakPath = (Get-Command plainspeak -ErrorAction SilentlyContinue).Source

    if ([string]::IsNullOrEmpty($PlainSpeakPath)) {
        Write-Host "Error: plainspeak command not found. Please install plainspeak first." -ForegroundColor Red
        exit 1
    }

    Write-Host "Creating pls.bat that calls plainspeak..."
    @"
@echo off
plainspeak %*
"@ | Out-File -FilePath "$UserBin\pls.bat" -Encoding ascii -Force
}

# Add to PATH if needed
$CurrentPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($CurrentPath -notlike "*$UserBin*") {
    Write-Host "Adding $UserBin to your PATH..."
    [Environment]::SetEnvironmentVariable("Path", "$CurrentPath;$UserBin", "User")

    # Also update current session
    $env:Path = "$env:Path;$UserBin"

    Write-Host "PATH updated for future sessions and current session."
} else {
    Write-Host "$UserBin is already in your PATH."
}

Write-Host ""
Write-Host "Installation complete!"
Write-Host "You can now use 'pls' as a friendly alternative to 'plainspeak'."
Write-Host "Example: pls ""convert all CSV files to JSON format"""
Write-Host ""
Write-Host "To verify the installation, run: pls --version"
