@echo off
REM Сборка exe для GTA 6: Blood Money.
REM Запускать из корня проекта (там, где лежит main.py).

c:\Users\melnikov_su\AppData\Roaming\Python\Python311\Scripts\pyinstaller.exe ^
    --noconfirm ^
    --clean ^
    --windowed ^
    --onefile ^
    --name "GTA6_Vice_Psyhopath" ^
    --add-data "assets;assets" ^
    main.py

echo.
echo Готово. Ищи dist\GTA6_Vice_Psyhopath.exe
pause
