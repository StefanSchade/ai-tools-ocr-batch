@echo off
REM Script to run the production Docker container

REM Check if data directory argument is provided
if "%1"=="" (
    echo Usage: run_prod_container.cmd [data_directory_path] [script_arguments...]
    exit /b 1
)

REM Get the absolute path of the data directory
set DATA_DIR=%~1

REM Shift the first argument (data directory) and pass the rest to the script
shift
set SCRIPT_ARGS=%*

REM Change to the project root directory
cd ..

REM Start the production container with additional script arguments
docker run -it --rm -v %DATA_DIR%:/app/data -w /app prod-environment %SCRIPT_ARGS%
pause
