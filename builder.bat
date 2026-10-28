@echo off
title Установка War Turtle
color 0A
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Запрос прав администратора...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo ========================================
echo      УСТАНОВКА War Turtle
echo ========================================
echo.
echo Проверка Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не найден!
    echo.
    echo Установите Python с: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)
echo [OK] Python найден
echo.
echo Проверка PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Установка PyInstaller...
    pip install pyinstaller
) else (
    echo [OK] PyInstaller уже установлен
)
echo.
if exist requirements.txt (
    echo Установка зависимостей...
    pip install -r requirements.txt
    echo.
)
echo Сборка War Turtle...
echo Это может занять несколько минут...
echo.

pyinstaller --onefile --windowed --name="WarTurtle" --icon="ico.ico" --add-data "assets;assets" main.py

if errorlevel 1 (
    echo.
    echo [ОШИБКА] Сборка не удалась!
    pause
    exit /b 1
)

echo.
echo ========================================
echo         ГОТОВО!
echo ========================================
echo.

echo Создание ярлыка...
set "exe_path=%CD%\dist\WarTurtle.exe"

powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\War Turtle.lnk'); $Shortcut.TargetPath = '%exe_path%'; $Shortcut.WorkingDirectory = '%CD%'; $Shortcut.Save()"

if errorlevel 1 (
    echo [ПРЕДУПРЕЖДЕНИЕ] Не удалось создать ярлык
) else (
    echo [OK] Ярлык создан на рабочем столе
)

echo.
echo [УСПЕХ] War Turtle собран!
echo Файл: dist\WarTurtle.exe
echo Ярлык: Рабочий стол
echo.
echo Нажмите любую клавишу для выхода...
pause >nul