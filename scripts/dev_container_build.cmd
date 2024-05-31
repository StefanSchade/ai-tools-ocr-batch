@echo off
REM Script to build the development Docker image
cd ..
docker build -t dev-environment .
pause
