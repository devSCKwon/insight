@echo off
chcp 65001 > nul
echo.
echo ==================================================
echo      암호화 파일 리스트 추출기 실행 스크립트 (Python)
echo ==================================================
echo.

REM 가상환경의 python 경로 설정 (프로젝트 루트 디렉토리 기준)
set PYTHON_PATH=..\.venv\Scripts\python.exe

if not exist "%PYTHON_PATH%" (
    echo [오류] 가상환경의 파이썬을 찾을 수 없습니다: %PYTHON_PATH%
    echo 루트 디렉터리에 가상환경(.venv)이 빌드되어 있는지 확인하세요.
    pause
    exit /b 1
)

echo ▶ 파이썬 스크립트를 실행합니다...
"%PYTHON_PATH%" decrypt_file_list.py

echo.
pause
