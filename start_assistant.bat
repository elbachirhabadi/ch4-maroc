@echo off
chcp 65001 >nul
title CH4 Maroc - Assistant IA (Groq)
color 0A

echo ============================================================
echo   Geoportail CH4 Maroc - Lancement Assistant IA (Groq)
echo ============================================================
echo.

REM ── 1. Verifier la cle API Groq ─────────────────────────────
if "%GROQ_API_KEY%"=="" (
    echo [1/2] Cle GROQ_API_KEY non definie.
    set /p GROQ_API_KEY="    Entre ta cle Groq (gsk_...): "
)
echo   OK - cle API configuree.
echo.

REM ── 2. Lancer le backend ────────────────────────────────────
echo [2/2] Demarrage du backend FastAPI sur http://localhost:8000
echo.
echo ============================================================
echo   Backend en cours d'execution sur http://localhost:8000
echo   Ouvre maintenant : geoportail-ch4\assistant.html
echo   Pour arreter : ferme cette fenetre ou appuie sur Ctrl+C
echo ============================================================
echo.

cd /d "%~dp0backend"
python -m uvicorn app:app --host 0.0.0.0 --port 8000

pause
