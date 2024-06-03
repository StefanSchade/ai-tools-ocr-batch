@echo off
REM Script to build the production Docker image
cd ..
docker build -f Dockerfile.prod -t prod-environment .
pause