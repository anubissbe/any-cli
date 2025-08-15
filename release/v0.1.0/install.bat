@echo off
REM Qwen Claude CLI Windows Installation Script
REM Version: 0.1.0

echo 🚀 Installing Qwen Claude CLI...

if not exist "qwen-claude-windows.exe" (
    echo ❌ Binary not found: qwen-claude-windows.exe
    echo Please ensure you're running this script from the release directory.
    pause
    exit /b 1
)

REM Default installation directory
set INSTALL_DIR=%USERPROFILE%\AppData\Local\Programs\Qwen Claude CLI
set INSTALL_PATH=%INSTALL_DIR%\qwen-claude.exe

REM Create install directory
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Copy binary
copy "qwen-claude-windows.exe" "%INSTALL_PATH%"

echo ✅ Installed to: %INSTALL_PATH%

echo.
echo ⚠️ Please add the following directory to your PATH:
echo    %INSTALL_DIR%
echo.
echo 🎉 Installation complete!
echo Run 'qwen-claude --help' to get started.
pause
