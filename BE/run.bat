@echo off
set PYTHONPATH=%CD%\TripScheduler
uvicorn app.main:app --reload