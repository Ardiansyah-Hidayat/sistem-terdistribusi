@echo off
title Ngrok Tunnel - Distributed Storage Remote Access
cd /d "%~dp0"
python start_ngrok.py
pause
