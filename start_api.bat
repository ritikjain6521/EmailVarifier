@echo off
echo Starting Email Verifier API...
python -m uvicorn app.main:app --reload
pause
