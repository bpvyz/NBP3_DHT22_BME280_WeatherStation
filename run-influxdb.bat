@echo off
SETLOCAL EnableDelayedExpansion

:: Title
echo InfluxDB Environment Setup
echo --------------------------

:: Check if Docker is running
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

:: Check for existing .env
if exist .env (
    echo WARNING: .env file already exists.
    choice /c yn /m "Do you want to overwrite it? (y/n)"
    if !errorlevel! equ 2 (
        echo Using existing .env file
        goto create_compose
    )
)

:: Get InfluxDB parameters from user
:get_url
set /p "influx_url=Enter InfluxDB url (default: http://localhost:8086/): "
if "!influx_url!"=="" set "influx_url=http://localhost:8086/"

:get_org
set /p "influx_org=Enter InfluxDB organization (default: nbp): "
if "!influx_org!"=="" set "influx_org=nbp"

:get_bucket
set /p "influx_bucket=Enter InfluxDB bucket (default: weatherstation): "
if "!influx_bucket!"=="" set "influx_bucket=weatherstation"

:get_user
set /p "influx_user=Enter admin username (default: admin): "
if "!influx_user!"=="" set "influx_user=admin"

:get_password
set /p "influx_pass=Enter admin password (min 8 chars): "
if "!influx_pass!"=="" (
    echo Password cannot be empty
    goto get_password
)
if "!influx_pass:~0,8!"=="!influx_pass!" (
    echo Password must be at least 8 characters
    goto get_password
)

:: Create .env file
(
    echo INFLUX_URL=!influx_url!
    echo INFLUX_ORG=!influx_org!
    echo INFLUX_BUCKET=!influx_bucket!
    echo INFLUX_USER=!influx_user!
    echo INFLUX_PASSWORD=!influx_pass!
) > .env

echo ✅ Created .env file with InfluxDB settings

:create_compose
:: Start InfluxDB with Docker Compose
echo Starting InfluxDB with Docker Compose...
docker-compose down -v
docker-compose up -d

if %errorlevel% equ 0 (
    echo.
    echo ✅ InfluxDB is now running at: http://localhost:8086
    echo Login with:
    echo Username: !influx_user!
    echo Password: (hidden)
    echo.
    echo Waiting for InfluxDB container to initialize...
    timeout /t 10 >nul

    :: Create token via InfluxDB CLI inside the container
    echo Creating token via InfluxDB CLI inside the container...

    :: Capture the output of the influx command and extract the token
    for /f "tokens=2" %%a in ('docker exec -it influxdb influx auth create --all-access') do (
        set influx_token=%%a
    )

    :: Check if the token was extracted correctly
    if not defined influx_token (
        echo ❌ ERROR: Failed to create token.
        pause
        exit /b 1
    )

    echo Token: !influx_token!

    :: Save token to .env file
    (for /f "usebackq delims=" %%l in (`findstr /v "^INFLUX_TOKEN=" .env`) do echo %%l) > tmp.env
    echo INFLUX_TOKEN=!influx_token!>> tmp.env
    move /Y tmp.env .env >nul

    echo ✅ Token saved to .env file.
    goto end
) else (
    echo.
    echo ❌ ERROR: Failed to start InfluxDB container.
    pause
    exit /b 1
)

:end
pause
ENDLOCAL
