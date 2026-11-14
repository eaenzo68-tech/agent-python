@echo off
rem Double-clique sur ce fichier pour lancer l'application sous Windows.
chcp 65001 >nul
cd /d "%~dp0"
title Agent Python - centre de formation

where py >nul 2>nul
if %errorlevel%==0 (
    py -3 serveur.py %*
    goto fin
)
where python >nul 2>nul
if %errorlevel%==0 (
    python serveur.py %*
    goto fin
)
echo Python est introuvable. Installe Python 3.12 depuis https://www.python.org/downloads/
echo (coche "Add python.exe to PATH" pendant l'installation).

:fin
pause
