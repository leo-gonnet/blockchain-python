Rem @echo off
Rem "C:\ProgramData\Anaconda3\python.exe" "C:\Users\Hp\Documents\TIPE\blockchain codes\node.py" -new_console:s75H
Rem PING localhost -n 3 >NUL
Rem "C:\ProgramData\Anaconda3\python.exe" "C:\Users\Hp\Documents\TIPE\blockchain codes\node.py" -new_console:s66H
Rem PING localhost -n 3 >NUL
Rem "python" "C:\Users\Hp\Documents\TIPE\blockchain codes\node.py" -new_console:s
cls
python "%~dp0simu.py" 1 -new_console:s50H
PING localhost -n 3 >NUL
cls
python "%~dp0simu.py" 0