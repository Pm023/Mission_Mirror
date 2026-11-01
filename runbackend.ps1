# PowerShell direct runner for Mission Mirror
$PSScriptRoot = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition
Set-Location -Path $PSScriptRoot

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  Launching MISSION MIRROR Server..." -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

python run.py

