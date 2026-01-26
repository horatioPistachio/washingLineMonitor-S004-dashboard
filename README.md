# washingLineMonitor-S004-dashboard

Dashboard for the washing line monitor. Links with backend in washingLineMonitor-S003-webserver.

## Features

- **Real-time Weather Display**: Shows current weather conditions including temperature, humidity, wind speed, and precipitation
- **Device Management**: View and manage all IoT devices with their status, location, and last activity
- **Notifications**: Monitor system alerts and device notifications from ntfy.sh
- **System Metrics**: Real-time system statistics from Glances (CPU, memory, disk usage)

## Setup

### Prerequisites

- Python 3.8+
- Access to the washingLineMonitor-S003-webserver API
- ntfy.sh topic for notifications

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd washingLineMonitor-S004-dashboard
```

2. Create a virtual environment:
```bash
python -m venv .venv
```

3. Activate the virtual environment:
- Windows: `.venv\Scripts\activate`
- Linux/Mac: `source .venv/bin/activate`

4. Install dependencies:
```bash
pip install streamlit pandas requests python-dotenv
```

5. Configure environment variables:
```bash
# Copy the example env file
cp .env.example .env

# Edit .env with your configuration
```

Required environment variables:
- `API_ENDPOINT`: Base URL for the washing line monitor API (default: http://washinglinemonitor-s003-webserver-app)
- `NTFY_TOPIC`: ntfy.sh topic for notifications (default: washingLineMonitor)
- `GLANCES_ENDPOINT`: Glances API endpoint for system statistics (default: http://localhost:61208)

### Running the Dashboard

**Local Development:**
```bash
streamlit run app.py
```

The dashboard will be available at `http://localhost:8501`

**Docker Deployment:**

1. Ensure the backend services (S003-webserver) are running:
```bash
cd washingLineMonitor-S003-webserver
docker-compose up -d
```

2. Start the dashboard:
```bash
cd washingLineMonitor-S004-dashboard
docker-compose up -d
```

3. Access the dashboard at `http://localhost:8501`

**Docker Commands:**
```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f dashboard

# Stop
docker-compose down

# Rebuild after code changes
docker-compose up -d --build
```

**Note:** The dashboard connects to backend services via Docker network. Both docker-compose files must be running for full functionality.

## API Integration

The dashboard integrates with the following API endpoints:

### Device Management
- `GET /api/v1/devices` - List all devices
- `GET /api/v1/devices/{device_id}` - Get device configuration
- `GET /api/v1/telemetry/{device_id}` - Get device telemetry data

### Notifications
- `GET https://ntfy.sh/{topic}/json?poll=1&since=24h` - Fetch notifications

### System Statistics
- `GET http://localhost:61208/api/3/all` - Glances API for system metrics (CPU, memory, disk)

## Backend Functions

### `fetch_notifications()`
Fetches recent notifications from ntfy.sh. Returns a DataFrame with timestamp, title, message, and device ID.

### `fetch_device_count()`
Returns the total number of registered devices in the system.

### `fetch_device_list()`
Fetches complete device information including:
- Device ID
- Location (from device configuration)
- Last active timestamp (from telemetry data)
- Status (Active/Inactive based on last activity within 1 hour)

This function makes concurrent requests to optimize performance when fetching data for multiple devices.

### `fetch_system_metrics()`
Fetches real-time system statistics from Glances API. Returns metrics for:
- Disk space usage (percentage and total GB)
- Memory usage (percentage and total GB)
- CPU load (percentage)

Returns default values (zeros) if Glances service is unavailable.

## Project Structure

```
washingLineMonitor-S004-dashboard/
├── app.py                      # Main Streamlit application
├── .prompts/                   # Prompt files for development
│   └── backend_data_pull.prompt.md
├── .env.example               # Example environment configuration
├── .gitignore
└── README.md
```

## Development

The dashboard is built with Streamlit and uses:
- **pandas** for data manipulation
- **requests** for API calls
- **concurrent.futures** for parallel API requests
- **datetime** for timestamp handling

## Troubleshooting

### API Connection Issues
- Verify the `API_ENDPOINT` is correct and the backend server is running
- Check network connectivity to the backend server
- Review the console output for error messages

### No Notifications Appearing
- Verify the `NTFY_TOPIC` matches the topic used by the backend
- Check that notifications are being sent to ntfy.sh
- Test the topic directly at https://ntfy.sh/{your-topic}

### Device Status Shows "Unknown"
- Ensure devices have sent telemetry data recently
- Check that device configurations include location information
- Verify the telemetry endpoint is returning data

### System Statistics Show "--"
- Verify Glances service is running on port 61208
- Check that `GLANCES_ENDPOINT` environment variable is correct
- Test the Glances API directly at http://localhost:61208/api/3/all
- Ensure no firewall is blocking access to Glances

## License

[Add license information here]

