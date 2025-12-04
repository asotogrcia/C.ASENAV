@echo off
TITLE INSTALADOR DE ARRANQUE AUTOMATICO - ASENAV
COLOR 1F

echo ================================================================
echo      CONFIGURANDO INICIO AUTOMATICO DE WINDOWS
echo ================================================================
echo.

:: 1. Definir rutas
:: %~dp0 es la carpeta actual donde está este archivo
set "RUTA_PROYECTO=%~dp0"
set "SCRIPT_OBJETIVO=%~dp0iniciar_sistema.bat"
set "NOMBRE_ACCESO_DIRECTO=Iniciar Servidor ASENAV.lnk"

:: 2. Definir la carpeta de Inicio de Windows del usuario actual
set "CARPETA_INICIO=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

echo Ruta del Proyecto: %RUTA_PROYECTO%
echo Script a ejecutar: %SCRIPT_OBJETIVO%
echo Carpeta Inicio:    %CARPETA_INICIO%
echo.

:: 3. Crear el Acceso Directo usando PowerShell
:: Esto es necesario porque BAT no puede crear .lnk nativamente
echo Creando acceso directo...

powershell "$s=(New-Object -COM WScript.Shell).CreateShortcut('%CARPETA_INICIO%\%NOMBRE_ACCESO_DIRECTO%');$s.TargetPath='%SCRIPT_OBJETIVO%';$s.WorkingDirectory='%RUTA_PROYECTO%';$s.IconLocation='%SystemRoot%\system32\SHELL32.dll,238';$s.Description='Arranca el servidor Django ASENAV';$s.Save()"

if %ERRORLEVEL% EQU 0 (
    COLOR 0A
    echo.
    echo [EXITO] El sistema se iniciara automaticamente al encender el PC.
    echo Se ha creado el archivo en:
    echo %CARPETA_INICIO%\%NOMBRE_ACCESO_DIRECTO%
) else (
    COLOR 0C
    echo [ERROR] No se pudo crear el acceso directo.
    echo Intente ejecutar este archivo como Administrador.
)

echo.
pause