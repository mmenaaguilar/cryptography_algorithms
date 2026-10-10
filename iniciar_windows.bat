@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  py -3 -m venv .venv
  if errorlevel 1 goto error
)
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto error
echo Abre http://127.0.0.1:5010 en tu navegador.
.venv\Scripts\python.exe app.py --port 5010
if errorlevel 1 (
  echo No se pudo iniciar. Si el puerto 5010 esta ocupado, cierra el servidor anterior.
  pause
)
exit /b
:error
echo No se pudo preparar el entorno. Consulta documentacion\Manual_usuario.docx.
pause
