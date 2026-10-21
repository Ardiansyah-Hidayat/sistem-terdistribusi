@echo off
title START - Distributed Storage System (VM Mode)
cd /d "%~dp0"
set CLUSTER_MODE=vm
python START_ALL.py
pause
