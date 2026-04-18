@echo off
echo Starting Email Verifier API from back-end folder...
python -m uvicorn app.main:app --reload
pause
