@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

rem ------------------------------------------------------------------ #
rem virusShare - one-shot Windows release build
rem
rem   1. preflight      python, dependencies (venv), Inno Setup
rem   2. clean          build\ and previous dist artifacts
rem   3. test gate      full pytest suite - a broken tree is never packaged
rem   4. assets         icon + version resource (idempotent)
rem   5. exe            PyInstaller onedir  -> dist\virusShare\virusShare.exe
rem   6. verify exe     --version + smoke launch
rem   7. installer      Inno Setup           -> dist\installer\virusShare-Setup.exe
rem   8. verify setup   file exists, non-trivial size
rem ------------------------------------------------------------------ #

echo === virusShare release build ===

set "VENV=.venv"
set "PY=%VENV%\Scripts\python.exe"
set "EXE=dist\virusShare\virusShare.exe"
set "SETUP=dist\installer\virusShare-Setup.exe"

rem ------------------------------ preflight ------------------------------ #
where python >nul 2>nul
if errorlevel 1 (
    echo [error] Python was not found on PATH.
    exit /b 1
)

if not exist "%PY%" (
    echo [1/8] Creating virtual environment in %VENV% ...
    python -m venv --system-site-packages "%VENV%"
    if errorlevel 1 (
        echo [error] venv creation failed.
        exit /b 1
    )
) else (
    echo [1/8] Reusing existing virtual environment %VENV%.
)

"%PY%" -m pip install --quiet --disable-pip-version-check --upgrade pip
if errorlevel 1 (
    echo [error] pip upgrade failed.
    exit /b 1
)

"%PY%" -m pip install --quiet --disable-pip-version-check -r requirements.txt -r requirements-dev.txt pyinstaller
if errorlevel 1 (
    echo [error] dependency installation failed.
    exit /b 1
)

set "ISCC="
if exist "%LocalAppData%\Programs\Inno Setup 6\ISCC.exe" set "ISCC=%LocalAppData%\Programs\Inno Setup 6\ISCC.exe"
if not defined ISCC if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not defined ISCC if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
where ISCC.exe >nul 2>nul
if not defined ISCC for /f "delims=" %%I in ('where ISCC.exe 2^>nul') do if not defined ISCC set "ISCC=%%I"
if not defined ISCC (
    echo [error] Inno Setup 6 ^(ISCC.exe^) was not found.
    echo         Install it first:  winget install JRSoftware.InnoSetup
    exit /b 1
)

rem -------------------------------- clean -------------------------------- #
echo [2/8] Cleaning previous build output...
if exist build rmdir /s /q build
if exist dist\virusShare rmdir /s /q dist\virusShare
if exist dist\installer rmdir /s /q dist\installer
if exist dist\virusShare-Setup.exe del /q dist\virusShare-Setup.exe
if exist dist\virusShare.exe del /q dist\virusShare.exe

rem ------------------------------ test gate ------------------------------ #
echo [3/8] Running full test suite (gate)...
"%PY%" -m pytest tests -q
if errorlevel 1 (
    echo [error] tests failed - refusing to package a broken build.
    exit /b 1
)

rem -------------------------------- assets ------------------------------- #
echo [4/8] Generating icon and version resource...
"%PY%" scripts\make_release_assets.py --force
if errorlevel 1 (
    echo [error] release asset generation failed.
    exit /b 1
)

rem ------------------------------ build exe ------------------------------ #
echo [5/8] Building executable ^(PyInstaller onedir^)...
"%PY%" -m PyInstaller --clean --noconfirm virusShare.spec
if errorlevel 1 (
    echo [error] PyInstaller build failed.
    exit /b 1
)
if not exist "%EXE%" (
    echo [error] expected output missing: %EXE%
    exit /b 1
)

rem ----------------------------- verify exe ------------------------------ #
echo [6/8] Verifying executable...
for /f "delims=" %%V in ('"%EXE%" --version') do set "VERSION_OUT=%%V"
echo         --version -^> !VERSION_OUT!
echo !VERSION_OUT! | findstr /c:"virusShare" >nul
if errorlevel 1 (
    echo [error] exe did not report its version.
    exit /b 1
)

rem --------------------------- build installer --------------------------- #
echo [7/8] Building installer ^(Inno Setup^)...
"%ISCC%" /Q installer\virusShare.iss
if errorlevel 1 (
    echo [error] Inno Setup compilation failed.
    exit /b 1
)

rem --------------------------- verify installer -------------------------- #
echo [8/8] Verifying installer...
if not exist "%SETUP%" (
    echo [error] expected output missing: %SETUP%
    exit /b 1
)
for %%F in ("%SETUP%") do set "SETUP_SIZE=%%~zF"
if %SETUP_SIZE% LSS 10000000 (
    echo [error] installer looks too small ^(%SETUP_SIZE% bytes^).
    exit /b 1
)

echo.
echo === build complete ===
echo.
echo     app      : %EXE%
echo     installer: %SETUP%  (%SETUP_SIZE% bytes)
echo     version  : !VERSION_OUT!
echo.
echo Notes:
echo   - installer registers virusShare for all users ^(requires admin^)
echo   - first launch creates %%LOCALAPPDATA%%\virusShare (settings, identity,
echo     trust store, data\history.db and logs\)
echo   - allow virusShare on Private networks in Windows Firewall
echo     for UDP 54321 / TCP 54322 transfer traffic
exit /b 0
