@echo off
setlocal EnableExtensions
title Caquot
pushd "%~dp0"
if errorlevel 1 goto :err_dossier

rem Environnement deja installe et a jour ?
rem Le temoin est une copie des fichiers requirements de la derniere installation reussie.
if not exist ".venv\caquot_ok.txt" goto :installer
copy /b requirements.txt + requirements-torch.txt "%TEMP%\caquot_req.txt" >nul
fc /b "%TEMP%\caquot_req.txt" ".venv\caquot_ok.txt" >nul 2>&1
if errorlevel 1 goto :installer
goto :lancer

:installer
rem Recherche d'un Python compatible : 3.12 a 3.14, 64 bits
set "PY="
for %%V in (3.14 3.13 3.12) do if not defined PY call :tester_python "py -%%V"
if not defined PY call :tester_python "python"
if not defined PY goto :err_python

echo.
echo  Premier lancement : installation de Caquot.
echo  Duree : 5 a 20 minutes selon votre connexion. Espace : environ 1 Go.
echo  Ne fermez pas cette fenetre.
echo.
%PY% -c "import os, sys; sys.exit(1 if len(os.getcwd()) > 67 else 0)"
if errorlevel 1 call :avert_chemin
if exist ".venv" rmdir /s /q ".venv"
%PY% -m venv .venv
if errorlevel 1 goto :err_install
set "VPY=.venv\Scripts\python.exe"
"%VPY%" -m pip install --upgrade pip
if errorlevel 1 goto :err_install

rem Carte graphique NVIDIA : PyTorch avec acceleration
where nvidia-smi >nul 2>&1
if errorlevel 1 goto :dependances
echo  Carte NVIDIA detectee : installation de PyTorch avec acceleration
echo  graphique. Ce telechargement pese plusieurs Go.
"%VPY%" -m pip install -r requirements-torch.txt --index-url https://download.pytorch.org/whl/cu130
if errorlevel 1 echo  [INFO] Acceleration graphique indisponible : Caquot utilisera le processeur.

:dependances
"%VPY%" -m pip install -r requirements-torch.txt -r requirements.txt
if errorlevel 1 goto :err_install
copy /b requirements.txt + requirements-torch.txt ".venv\caquot_ok.txt" >nul

:lancer
".venv\Scripts\python.exe" -m caquot.main
if errorlevel 1 goto :err_execution
goto :fin

:tester_python
%~1 -c "import sys; sys.exit(0 if (3,12) <= sys.version_info[:2] <= (3,14) and sys.maxsize > 2**32 else 1)" >nul 2>&1
if not errorlevel 1 set "PY=%~1"
exit /b 0

:avert_chemin
echo.
echo  [ATTENTION] Le dossier de Caquot est range dans un chemin long.
echo  L'installation risque d'echouer. Conseil : fermez cette fenetre,
echo  deplacez le dossier dans un emplacement court comme C:\Caquot,
echo  puis relancez. Pour essayer quand meme, appuyez sur une touche.
pause >nul
exit /b 0

:err_python
echo.
echo  [ERREUR] Python 3.12, 3.13 ou 3.14 en 64 bits est introuvable.
echo.
echo   1. Ouvrez le Microsoft Store, cherchez "Python Install Manager"
echo      et installez-le.
echo   2. Ouvrez le Terminal et tapez :   py install 3.14
echo   3. Relancez ce fichier.
echo.
echo  Detail dans le fichier README, section Installation sous Windows.
goto :fin

:err_install
echo.
echo  [ERREUR] L'installation n'a pas abouti.
echo  Causes frequentes :
echo    - connexion internet coupee ou filtree par l'etablissement ;
echo    - dossier range dans un chemin trop long : deplacez-le dans un
echo      emplacement court, par exemple C:\Caquot ;
echo    - espace disque insuffisant.
echo  Corrigez puis relancez ce fichier : l'installation reprendra.
goto :fin

:err_execution
echo.
echo  [ERREUR] Caquot s'est arrete sur une erreur. Le message ci-dessus
echo  aide a comprendre pourquoi : copiez-le pour demander de l'aide.
goto :fin

:err_dossier
echo  [ERREUR] Impossible d'ouvrir le dossier de Caquot.

:fin
popd
echo.
pause
endlocal