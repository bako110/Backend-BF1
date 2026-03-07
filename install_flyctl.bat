@echo off
echo Téléchargement de Fly CLI...

REM Créer le dossier pour Fly CLI
if not exist "%USERPROFILE%\flyctl" mkdir "%USERPROFILE%\flyctl"

REM Télécharger flyctl.exe directement
powershell -Command "& {Invoke-WebRequest -Uri 'https://github.com/superfly/flyctl/releases/latest/download/flyctl_windows_amd64.tar.gz' -OutFile '%USERPROFILE%\flyctl\flyctl.tar.gz'}"

REM Ajouter au PATH utilisateur (temporaire)
set PATH=%PATH%;%USERPROFILE%\flyctl

echo.
echo Fly CLI téléchargé !
echo Vous pouvez maintenant utiliser 'flyctl' ou 'fly' dans ce terminal.
echo.
echo Pour une installation permanente, ajoutez %USERPROFILE%\flyctl à votre PATH système.

pause