@echo off
title SHUTDOWN - Distributed Storage System
cd /d "%~dp0"
python stop_all.py
pause
