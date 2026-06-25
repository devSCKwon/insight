@echo off
chcp 65001 > nul
echo.
echo ==================================================
echo       암호화 파일 리스트 추출기 EXE 빌드 스크립트
echo ==================================================
echo.

REM 가상환경의 pyinstaller 경로 설정 (프로젝트 루트 디렉토리 기준)
set PYINSTALLER_PATH=..\.venv\Scripts\pyinstaller.exe

if not exist "%PYINSTALLER_PATH%" (
    echo [오류] 가상환경의 PyInstaller를 찾을 수 없습니다: %PYINSTALLER_PATH%
    echo 루트 디렉터리에 가상환경(.venv)이 빌드되어 있는지 확인하세요.
    pause
    exit /b 1
)

echo ▶ PyInstaller를 사용하여 빌드를 시작합니다...
"%PYINSTALLER_PATH%" --onefile --clean --name decrypt_file_list decrypt_file_list.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo [오류] 빌드 중 에러가 발생했습니다.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ▶ 빌드가 완료되었습니다!
echo ▶ 생성된 실행 파일을 현재 디렉터리로 복사합니다.
copy /y dist\decrypt_file_list.exe .\decrypt_file_list.exe

echo ▶ 빌드 임시 폴더 및 파일을 정리합니다...
rd /s /q build
rd /s /q dist
del /q decrypt_file_list.spec

echo.
echo ==================================================
echo 빌드가 성공적으로 완료되었습니다.
echo 현재 폴더의 [decrypt_file_list.exe] 파일과 [config.ini]를
echo 원하는 위치에 함께 복사하여 사용할 수 있습니다.
echo ==================================================
echo.
pause
