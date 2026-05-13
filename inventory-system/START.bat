@echo off
chcp 65001 >nul
echo =========================================
echo  다점포 실시간 재고관리 시스템 시작
echo =========================================
echo.

:: 가상환경 생성 (최초 1회)
if not exist venv (
    echo [1/3] 가상환경 생성 중...
    python -m venv venv
)

:: 패키지 설치
echo [2/3] 패키지 설치 중...
call venv\Scripts\activate.bat
pip install -r requirements.txt --quiet

:: 서버 실행
echo [3/3] Flask 서버 시작...
echo.
echo  브라우저에서 http://localhost:5000 으로 접속하세요
echo  종료하려면 Ctrl+C 를 누르세요
echo.
python app.py
pause
