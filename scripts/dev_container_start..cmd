@echo off
REM Script to start the Docker container for development

REM Check if data directory argument is provided
if "%1"=="" (
    echo Usage: dev_start_container.cmd [data_directory_path]
    exit /b 1
)

REM Get the absolute path of the data directory
set DATA_DIR=%~1

REM Change to the project root directory
cd ..

REM Start the development container
docker run -it --rm -v %DATA_DIR%:/workspace/data -v %cd%/src:/workspace/src -w /workspace dev-environment
pause
