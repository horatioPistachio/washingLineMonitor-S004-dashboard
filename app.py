import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="IoT Fleet Manager",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
    <style>
    /* Reduce default streamlit padding */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 100%;
    }
    .weather-header {
        background: linear-gradient(135deg, #2176FF 0%, #1557b0 100%);
        padding: 18px 24px;
        border-radius: 8px;
        color: white;
        margin-bottom: 15px;
        margin-top: -10px;
    }
    h1, h2, h3 {
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .stProgress > div > div > div > div {
        background-color: #2176FF;
    }
    /* Compact dataframe */
    .stDataFrame {
        font-size: 0.9rem;
    }
    /* Reduce hr spacing */
    hr {
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
    }
    /* Radio button bubble styling */
    .stRadio > div {
        gap: 0.5rem;
        display: flex;
        flex-direction: column;
        width: 100%;
    }
    .stRadio > div > label {
        background-color: transparent;
        border-radius: 20px;
        padding: 12px 20px;
        border: 1px solid #e0e0e0;
        transition: all 0.3s ease;
        cursor: pointer;
        display: block;
        width: 100%;
        text-align: center;
    }
    .stRadio > div > label:hover {
        background-color: #f0f0f0;
        border-color: #2176FF;
    }
    .stRadio > div > label[data-baseweb="radio"] > div:first-child {
        display: none;
    }
    .stRadio > div > label > div {
        padding-left: 0 !important;
    }
    /* Style for selected radio button - multiple selectors for compatibility */
    .stRadio > div > label:has(input:checked),
    .stRadio > div > label[data-checked="true"],
    div[role="radiogroup"] label:has(input:checked) {
        background-color: #2176FF !important;
        color: white !important;
        border-color: #2176FF !important;
    }
    /* Ensure text color is white when selected */
    .stRadio > div > label:has(input:checked) > div,
    .stRadio > div > label[data-checked="true"] > div,
    div[role="radiogroup"] label:has(input:checked) > div {
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# API INTEGRATION FUNCTIONS (TO BE IMPLEMENTED)
# ============================================================================

@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_weather_data():
    """
    Fetch weather data from API
    Cached for 5 minutes to reduce API calls
    """

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": -26.829099,      # Latitude for Sydney
        "longitude": 153.043996,     # Longitude for Sydney
        "current": "temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m",
        "hourly": "temperature_2m,rain",
        "timezone": "auto",
        "models": "best_match" # OPTIONAL: Explicitly requests BOM's model
    }

    wmo_codes = {
        0: "Clear Sky",
        1: "Mainly Clear",
        2: "Partly Cloudy",
        3: "Overcast",
        45: "Fog",
        51: "Drizzle",
        61: "Slight Rain",
        80: "Rain Showers"
    }

    # 2. Make the request
    try:
        response = requests.get(url, params=params, timeout=5)

        # 3. Handle the response
        if response.status_code == 200:
            data = response.json()
            current = data['current']
            
            return {
                "temperature": current.get('temperature_2m', '--'),
                "condition": wmo_codes.get(current.get('weather_code', 0), "--"),
                "wind_speed": current.get('wind_speed_10m', '--'),
                "precipitation": current.get('precipitation', '--'),
                "humidity": current.get('relative_humidity_2m', '--'),
                "location": "Banya"
            }
        else:
            print(f"Error fetching data: Status code {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
    
    # Return default values if API call fails
    return {
        "temperature": "--",
        "condition": "--",
        "wind_speed": "--",
        "precipitation": "--",
        "humidity": "--",
        "location": "Banya"
    }

@st.cache_data(ttl=60)  # Cache for 60 seconds
def fetch_notifications():
    """
    Fetch recent notifications from ntfy.sh API
    Returns a DataFrame with TIMESTAMP, TITLE, MESSAGE, DEVICE ID columns
    Cached for 60 seconds to reduce API calls
    """
    import os
    
    # Get topic from environment variable or use default
    topic = os.environ.get('NTFY_TOPIC', 'washingLineMonitor')
    url = f"https://ntfy.sh/{topic}/json?poll=1&since=latest"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"NTFY Response Text: {response.text}")
        print(f"NTFY Response Status Code: {response.status_code}")
        if response.status_code == 200:
            # Parse response - ntfy returns newline-delimited JSON
            notifications = []
            for line in response.text.strip().split('\n'):
                if line:
                    try:
                        notif = eval(line)  # ntfy returns JSON per line
                        notifications.append(notif)
                    except:
                        pass
            
            if notifications:
                # Convert to DataFrame format
                df_data = {
                    "TIMESTAMP": [],
                    "TITLE": [],
                    "MESSAGE": [],
                    "DEVICE ID": []
                }
                
                for notif in notifications:
                    # Convert Unix timestamp to readable format
                    timestamp = datetime.fromtimestamp(notif.get('time', 0))
                    df_data["TIMESTAMP"].append(timestamp.strftime("%Y-%m-%d %H:%M:%S"))
                    df_data["TITLE"].append(notif.get('title', 'N/A'))
                    df_data["MESSAGE"].append(notif.get('message', ''))
                    # Try to extract device ID from message if present
                    message = notif.get('message', '')
                    device_id = "--"
                    if "Device " in message:
                        # Extract device ID from message like "Device device_001 reported..."
                        parts = message.split("Device ")
                        if len(parts) > 1:
                            device_id = parts[1].split()[0]
                    df_data["DEVICE ID"].append(device_id)
                
                return pd.DataFrame(df_data)
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching notifications: {e}")
    except Exception as e:
        print(f"Error processing notifications: {e}")
    
    # Return empty DataFrame on failure
    return pd.DataFrame({
        "TIMESTAMP": [],
        "TITLE": [],
        "MESSAGE": [],
        "DEVICE ID": []
    })

@st.cache_data(ttl=10)  # Cache for 10 seconds
def fetch_system_metrics():
    """
    Fetch real-time system metrics from Glances API
    Returns dict with disk, memory, and CPU metrics
    Cached for 10 seconds to reduce API calls
    """
    import os
    
    endpoint = os.environ.get('GLANCES_ENDPOINT', 'http://localhost:61208')
    url = f"{endpoint}/api/4/all"
    
    try:
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract disk metrics (first filesystem)
            fs_list = data.get('fs', [])
            disk_info = fs_list[0] if fs_list else {}
            disk_size_gb = disk_info.get('size', 0) / (1024**3)
            disk_percent = disk_info.get('percent', 0)
            
            # Extract memory metrics
            mem = data.get('mem', {})
            mem_total_gb = mem.get('total', 0) / (1024**3)
            mem_percent = mem.get('percent', 0)
            
            # Extract CPU metrics
            cpu = data.get('cpu', {})
            cpu_percent = cpu.get('total', 0)
            
            return {
                "disk": {
                    "percentage": disk_percent,
                    "total_gb": disk_size_gb
                },
                "memory": {
                    "percentage": mem_percent,
                    "total_gb": mem_total_gb
                },
                "cpu": {
                    "percentage": cpu_percent
                }
            }
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Glances data: {e}")
    except Exception as e:
        print(f"Error processing Glances data: {e}")
    
    # Return default values on failure
    return {
        "disk": {"percentage": 0, "total_gb": 0},
        "memory": {"percentage": 0, "total_gb": 0},
        "cpu": {"percentage": 0}
    }

@st.cache_data(ttl=30)  # Cache for 30 seconds
def fetch_device_count():
    """
    Fetch total device count from API
    Returns the number of registered devices
    Cached for 30 seconds to reduce API calls
    """
    import os
    endpoint = os.environ.get('API_ENDPOINT', 'http://127.0.0.1:8000/')
    print(f"API_ENDPOINT: {endpoint}")
    url = f"{endpoint}/api/v1/devices"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            devices = response.json()
            return len(devices)
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching device count: {e}")
    except Exception as e:
        print(f"Error processing device count: {e}")
    
    # Return 0 on failure
    return 0

def create_device(device_id, configuration):
    """
    Create a new device via the API
    Returns tuple: (success: bool, message: str, status_code: int)
    """
    import os
    
    endpoint = os.environ.get('API_ENDPOINT', 'http://127.0.0.1:8000/')
    url = f"{endpoint}/api/v1/devices"
    
    try:
        payload = {
            "device_id": device_id,
            "configuration": configuration
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 201:
            return (True, f"Device '{device_id}' created successfully!", 201)
        elif response.status_code == 409:
            return (False, f"Device '{device_id}' already exists.", 409)
        elif response.status_code == 400:
            return (False, "Invalid request format. Please check your inputs.", 400)
        else:
            return (False, f"Unexpected error: Status code {response.status_code}", response.status_code)
    
    except requests.exceptions.RequestException as e:
        return (False, f"Network error: {str(e)}", 0)
    except Exception as e:
        return (False, f"Error creating device: {str(e)}", 0)

@st.cache_data(ttl=60)  # Cache for 60 seconds
def fetch_device_config(device_id):
    """
    Fetch device configuration from API
    Returns tuple: (success: bool, configuration: dict, message: str)
    Cached for 60 seconds to reduce API calls
    """
    import os
    
    endpoint = os.environ.get('API_ENDPOINT', 'http://127.0.0.1:8000/')
    url = f"{endpoint}/api/v1/devices/{device_id}"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            configuration = data.get('configuration', {})
            return (True, configuration, "Configuration retrieved successfully")
        elif response.status_code == 404:
            return (False, {}, f"Device '{device_id}' not found.")
        else:
            return (False, {}, f"Unexpected error: Status code {response.status_code}")
    
    except requests.exceptions.RequestException as e:
        return (False, {}, f"Network error: {str(e)}")
    except Exception as e:
        return (False, {}, f"Error fetching configuration: {str(e)}")

def update_device_config(device_id, configuration):
    """
    Update device configuration via the API
    Returns tuple: (success: bool, message: str, status_code: int)
    """
    import os
    
    endpoint = os.environ.get('API_ENDPOINT', 'http://127.0.0.1:8000/')
    url = f"{endpoint}/api/v1/devices/{device_id}"
    
    try:
        payload = {
            "device_id": device_id,
            "configuration": configuration
        }
        
        response = requests.patch(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            return (True, f"Device '{device_id}' updated successfully!", 200)
        elif response.status_code == 404:
            return (False, f"Device '{device_id}' not found.", 404)
        elif response.status_code == 400:
            return (False, "Invalid request format. Please check your inputs.", 400)
        else:
            return (False, f"Unexpected error: Status code {response.status_code}", response.status_code)
    
    except requests.exceptions.RequestException as e:
        return (False, f"Network error: {str(e)}", 0)
    except Exception as e:
        return (False, f"Error updating device: {str(e)}", 0)

def delete_device(device_id):
    """
    Delete a device via the API
    Returns tuple: (success: bool, message: str, status_code: int)
    """
    import os
    
    endpoint = os.environ.get('API_ENDPOINT', 'http://127.0.0.1:8000/')
    url = f"{endpoint}/api/v1/devices/{device_id}"
    
    try:
        response = requests.delete(url, timeout=10)
        
        if response.status_code == 204:
            return (True, f"Device '{device_id}' deleted successfully!", 204)
        elif response.status_code == 404:
            return (False, f"Device '{device_id}' not found.", 404)
        else:
            return (False, f"Unexpected error: Status code {response.status_code}", response.status_code)
    
    except requests.exceptions.RequestException as e:
        return (False, f"Network error: {str(e)}", 0)
    except Exception as e:
        return (False, f"Error deleting device: {str(e)}", 0)

@st.cache_data(ttl=30)  # Cache for 30 seconds
def fetch_telemetry_data(device_id, start_time=None, end_time=None):
    """
    Fetch telemetry data for a device within a time range
    
    Args:
        device_id: Device identifier
        start_time: datetime object for range start (optional)
        end_time: datetime object for range end (optional)
    
    Returns:
        tuple: (success: bool, data: list, message: str)
    
    Cached for 30 seconds to reduce API calls
    """
    import os
    
    endpoint = os.environ.get('API_ENDPOINT', 'http://127.0.0.1:8000/')
    url = f"{endpoint}/api/v1/telemetry/{device_id}"
    
    # Build query parameters
    params = {}
    if start_time:
        params['start_time'] = start_time.strftime("%Y-%m-%dT%H:%M:%S")
    if end_time:
        params['end_time'] = end_time.strftime("%Y-%m-%dT%H:%M:%S")
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return (True, data, "Data retrieved successfully")
        elif response.status_code == 404:
            return (False, [], f"Device '{device_id}' not found")
        else:
            return (False, [], f"Error: Status code {response.status_code}")
    
    except requests.exceptions.RequestException as e:
        return (False, [], f"Network error: {str(e)}")
    except Exception as e:
        return (False, [], f"Error: {str(e)}")

def process_telemetry_data(telemetry_records):
    """
    Process telemetry records into a DataFrame with local timestamps
    
    Returns:
        DataFrame with columns: timestamp, metric1, metric2, ...
    """
    if not telemetry_records:
        return pd.DataFrame()
    
    # Parse data
    rows = []
    for record in telemetry_records:
        row = {}
        
        # Convert UTC timestamp to local time
        timestamp_str = record['timestamp']
        timestamp_utc = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        timestamp_local = timestamp_utc.astimezone()
        row['timestamp'] = timestamp_local
        
        # Extract all payload metrics
        payload = record.get('payload', {})
        for key, value in payload.items():
            row[key] = value
        
        rows.append(row)
    
    df = pd.DataFrame(rows)
    
    # Sort by timestamp
    if not df.empty:
        df = df.sort_values('timestamp')
    
    return df

def convert_df_to_csv(df):
    """Convert DataFrame to CSV for download"""
    return df.to_csv(index=False).encode('utf-8')

@st.cache_data(ttl=30)  # Cache for 30 seconds
def fetch_device_list():
    """
    Fetch device list from API with complete information
    Combines data from /devices, /devices/{id}, and /telemetry/{id} endpoints
    Returns a DataFrame with DEVICE_ID, LOCATION, LAST_ACTIVE, STATUS columns
    Cached for 30 seconds to reduce API calls
    """
    import os
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    endpoint = os.environ.get('API_ENDPOINT', 'http://127.0.0.1:8000/')
    
    def fetch_device_details(device_id):
        """Fetch configuration and telemetry for a single device"""
        device_info = {
            "DEVICE_ID": device_id,
            "LOCATION": "Unknown",
            "LAST_ACTIVE": "--",
            "STATUS": "Unknown"
        }
        
        try:
            # Fetch device configuration for location
            config_response = requests.get(
                f"{endpoint}/api/v1/devices/{device_id}",
                timeout=10
            )
            
            if config_response.status_code == 200:
                config_data = config_response.json()
                configuration = config_data.get('configuration', {})
                device_info["LOCATION"] = configuration.get('location', 'Unknown')
            
            # Fetch telemetry data for last_active and status
            telemetry_response = requests.get(
                f"{endpoint}/api/v1/telemetry/{device_id}",
                timeout=10
            )
            
            if telemetry_response.status_code == 200:
                telemetry_data = telemetry_response.json()
                
                if telemetry_data and len(telemetry_data) > 0:
                    # Get latest timestamp (first item, as results are ordered DESC)
                    latest = telemetry_data[0]
                    timestamp_str = latest.get('timestamp', '')
                    
                    if timestamp_str:
                        # Parse timestamp
                        try:
                            last_active_dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                            device_info["LAST_ACTIVE"] = last_active_dt.strftime("%Y-%m-%d %H:%M:%S")
                            
                            # Determine status based on last activity
                            now = datetime.now(last_active_dt.tzinfo) if last_active_dt.tzinfo else datetime.now()
                            time_diff = now - last_active_dt
                            
                            if time_diff <= timedelta(hours=1):
                                device_info["STATUS"] = "Active"
                            else:
                                device_info["STATUS"] = "Inactive"
                        except Exception as e:
                            print(f"Error parsing timestamp for {device_id}: {e}")
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching details for device {device_id}: {e}")
        except Exception as e:
            print(f"Error processing device {device_id}: {e}")
        
        return device_info
    
    try:
        # Step 1: Fetch all device IDs
        response = requests.get(f"{endpoint}/api/v1/devices", timeout=10)
        
        if response.status_code == 200:
            devices_list = response.json()
            device_ids = [d.get('device_id') for d in devices_list if 'device_id' in d]
            
            # Step 2: Fetch details for each device concurrently
            devices = []
            with ThreadPoolExecutor(max_workers=5) as executor:
                future_to_device = {executor.submit(fetch_device_details, dev_id): dev_id 
                                  for dev_id in device_ids}
                
                for future in as_completed(future_to_device):
                    device_info = future.result()
                    devices.append(device_info)
            
            return pd.DataFrame(devices)
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching device list: {e}")
    except Exception as e:
        print(f"Error processing device list: {e}")
    
    # Return empty DataFrame on failure
    return pd.DataFrame(columns=["DEVICE_ID", "LOCATION", "LAST_ACTIVE", "STATUS"])

# ============================================================================
# SIDEBAR
# ============================================================================

# Check if viewing device page
query_params = st.query_params
viewing_device = query_params.get("page") == "device" and query_params.get("device_id")

with st.sidebar:
    st.title("📡 IoT Fleet Manager")
    
    if viewing_device:
        st.markdown("**Viewing Device Details**")
        if st.button("← Back to Dashboard"):
            st.query_params.clear()
            st.rerun()
    else:
        st.markdown("**Device Management**")
        st.markdown("---")
        
        # Navigation menu
      
        menu_selection = st.radio(
            "Navigation",
            ["Dashboard", "Devices"],
            index=0,
            label_visibility="collapsed"
        )
    
    st.markdown("---")
    
    # Total devices display
    device_count = fetch_device_count()
    st.markdown(f"### Total Devices")
    st.markdown(f"# {device_count}")

# ============================================================================
# MAIN CONTENT
# ============================================================================

# Check if viewing device page
if viewing_device:
    device_id = query_params.get("device_id")
    
    # Device page header
    col_title, col_refresh = st.columns([6, 1])
    with col_title:
        st.markdown(f"### Device {device_id}")
    with col_refresh:
        if st.button("🔄 Refresh", key="refresh_device_detail"):
            st.cache_data.clear()
            st.rerun()
    
    # Fetch device config for location
    success, config, message = fetch_device_config(device_id)
    location = config.get('location', 'Unknown') if success else 'Unknown'
    
    # Time range options
    time_ranges = {
        "Last 1 Hour": timedelta(hours=1),
        "Last 6 Hours": timedelta(hours=6),
        "Last 12 Hours": timedelta(hours=12),
        "Last 24 Hours": timedelta(hours=24),
        "Last 7 Days": timedelta(days=7),
        "Last 30 Days": timedelta(days=30)
    }
    
    selected_range = st.selectbox("Time Range", list(time_ranges.keys()), index=3)
    time_delta = time_ranges[selected_range]
    
    # Calculate time range
    end_time = datetime.now()
    start_time = end_time - time_delta
    
    # Fetch telemetry data
    with st.spinner("Loading telemetry data..."):
        success, telemetry_data, message = fetch_telemetry_data(device_id, start_time, end_time)
    
    if not success:
        st.error(message)
        df = pd.DataFrame()
    else:
        df = process_telemetry_data(telemetry_data)
    
    # Header info in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("**Device ID**")
        st.markdown(device_id)
    
    with col2:
        st.markdown("**Location**")
        st.markdown(location)
    
    with col3:
        st.markdown("**Last Activity**")
        if not df.empty:
            last_activity = df['timestamp'].max()
            st.markdown(last_activity.strftime("%Y-%m-%d %H:%M:%S"))
        else:
            st.markdown("--")
    
    with col4:
        st.markdown("**Status**")
        if not df.empty:
            last_activity = df['timestamp'].max()
            now = datetime.now(last_activity.tzinfo)
            time_diff = now - last_activity
            status = "🟢 Active" if time_diff <= timedelta(hours=1) else "🔴 Inactive"
            st.markdown(status)
        else:
            st.markdown("--")
    
    st.markdown("---")
    
    # Download button
    if not df.empty:
        csv_data = convert_df_to_csv(df)
        st.download_button(
            label="📅 Download CSV",
            data=csv_data,
            file_name=f"{device_id}_telemetry_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            type="primary"
        )
    
    st.markdown("---")
    
    # Plots section
    if df.empty:
        st.info("No telemetry data available for the selected time range.")
    else:
        st.markdown("**Telemetry Data**")
        
        metric_columns = [col for col in df.columns if col != 'timestamp']
        
        if not metric_columns:
            st.warning("No metrics found in telemetry data")
        else:
            for metric in metric_columns:
                st.markdown(f"#### {metric.replace('_', ' ').title()}")
                plot_df = df[['timestamp', metric]].copy().set_index('timestamp')
                st.line_chart(plot_df, use_container_width=True)

elif menu_selection == "Dashboard":
    # Refresh button
    col_title, col_refresh = st.columns([6, 1])
    with col_title:
        st.markdown("### Dashboard")
    with col_refresh:
        if st.button("🔄 Refresh", key="refresh_dashboard"):
            st.cache_data.clear()
            st.rerun()
    
    st.markdown("---")
    
    # Weather Header
    weather_data = fetch_weather_data()

    st.markdown(f"""
        <div class="weather-header">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="font-size: 42px; font-weight: bold;">☀️ {weather_data['temperature']}°C</span>
                    <span style="margin-left: 15px; font-size: 16px;">{weather_data['condition']}</span>
                </div>
                <div style="display: flex; gap: 25px; align-items: center; font-size: 15px;">
                    <div>💨 {weather_data['wind_speed']} km/h</div>
                    <div>🌧️ {weather_data['precipitation']}%</div>
                    <div>💧 Humidity {weather_data['humidity']}%</div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 12px; opacity: 0.9;">Location</div>
                    <div style="font-weight: bold; font-size: 15px;">{weather_data['location']}</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Recent Notifications Section
    st.markdown("### Recent Notifications")
    notifications_df = fetch_notifications()  # API call placeholder
    st.dataframe(
        notifications_df,
        width='stretch',
        hide_index=True,
        height=220
    )

    # System State Section
    st.markdown("**System State**")

    # Fetch metrics data from Glances
    metrics = fetch_system_metrics()

    # Create 3 columns for metrics
    col1, col2, col3 = st.columns(3)

    # Metric 1: Disk Space Usage
    with col1:
        st.markdown("<small>Disk Space Usage</small>", unsafe_allow_html=True)
        disk = metrics["disk"]
        if disk["total_gb"] > 0:
            st.markdown(f"### {disk['percentage']:.1f}% <small>of {disk['total_gb']:.0f} GB</small>", unsafe_allow_html=True)
            st.progress(disk['percentage'] / 100)
        else:
            st.markdown("### --")
            st.markdown("<small>:orange[Glances unavailable]</small>", unsafe_allow_html=True)

    # Metric 2: Memory Usage
    with col2:
        st.markdown("<small>Memory Usage</small>", unsafe_allow_html=True)
        mem = metrics["memory"]
        if mem["total_gb"] > 0:
            st.markdown(f"### {mem['percentage']:.1f}% <small>of {mem['total_gb']:.1f} GB</small>", unsafe_allow_html=True)
            st.progress(mem['percentage'] / 100)
        else:
            st.markdown("### --")
            st.markdown("<small>:orange[Glances unavailable]</small>", unsafe_allow_html=True)

    # Metric 3: CPU Load
    with col3:
        st.markdown("<small>CPU Load</small>", unsafe_allow_html=True)
        cpu = metrics["cpu"]
        if cpu["percentage"] > 0:
            st.markdown(f"### {cpu['percentage']:.1f}%", unsafe_allow_html=True)
            # Color coding based on load
            color = "green" if cpu["percentage"] < 60 else "orange" if cpu["percentage"] < 80 else "red"
            st.markdown(f"<small>:{color}[Current load]</small>", unsafe_allow_html=True)
        else:
            st.markdown("### --")
            st.markdown("<small>:orange[Glances unavailable]</small>", unsafe_allow_html=True)
    
    # Link to Glances web interface
    glances_url = os.environ.get('GLANCES_ENDPOINT', 'http://localhost:61208')
    st.markdown(f"[📊 View Detailed System Stats]({glances_url})")

elif menu_selection == "Devices":
    # Device Management Page
    col_title, col_refresh = st.columns([6, 1])
    with col_title:
        st.markdown("### Device Management")
    with col_refresh:
        if st.button("🔄 Refresh", key="refresh_devices"):
            st.cache_data.clear()
            st.rerun()
    
    st.markdown("---")
    
    # Fetch device data
    devices_df = fetch_device_list()  # API call placeholder
    if not devices_df.empty:
        # Device Summary Metrics
        total_devices = len(devices_df)
        active_devices = len(devices_df[devices_df['STATUS'] == 'Active'])
    else:
        total_devices = 0
        active_devices = 0
    
    # Create 2 columns for summary metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<small>Total Devices</small>", unsafe_allow_html=True)
        st.markdown(f"### {total_devices}", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<small>Active Devices</small>", unsafe_allow_html=True)
        st.markdown(f"### {active_devices}", unsafe_allow_html=True)
        active_percentage = (active_devices / total_devices * 100) if total_devices > 0 else 0
        color = "green" if active_percentage >= 60 else "orange" if active_percentage >= 40 else "red"
        st.markdown(f"<small>:{color}[{active_percentage:.1f}% of total devices]</small>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Action Button and Form
    if 'show_add_form' not in st.session_state:
        st.session_state.show_add_form = False
    
    if st.button("➕ Add New Device", type="primary"):
        st.session_state.show_add_form = not st.session_state.show_add_form
    
    # Add Device Form
    if st.session_state.show_add_form:
        with st.expander("Add New Device", expanded=True):
            with st.form(key="add_device_form"):
                new_device_id = st.text_input(
                    "Device ID *",
                    placeholder="e.g., device_001",
                    help="Enter a unique identifier for the device"
                )
                
                new_config_json = st.text_area(
                    "Configuration (JSON) *",
                    placeholder='{"location": "Backyard", "sensor_type": "temperature"}',
                    height=120,
                    help="Enter device configuration as valid JSON"
                )
                
                col_submit, col_cancel = st.columns([1, 1])
                
                with col_submit:
                    submit_button = st.form_submit_button("Create Device", type="primary")
                
                with col_cancel:
                    cancel_button = st.form_submit_button("Cancel")
                
                if cancel_button:
                    st.session_state.show_add_form = False
                    st.rerun()
                
                if submit_button:
                    # Validation
                    errors = []
                    
                    # Check if device ID is empty
                    if not new_device_id or not new_device_id.strip():
                        errors.append("Device ID is required")
                    
                    # Check if configuration is empty
                    if not new_config_json or not new_config_json.strip():
                        errors.append("Configuration is required")
                    
                    # Validate JSON
                    config_dict = None
                    if new_config_json and new_config_json.strip():
                        try:
                            import json
                            config_dict = json.loads(new_config_json)
                        except json.JSONDecodeError as e:
                            errors.append(f"Invalid JSON: {str(e)}")
                    
                    # Display errors or create device
                    if errors:
                        for error in errors:
                            st.error(error)
                    else:
                        # Create device via API
                        with st.spinner("Creating device..."):
                            success, message, status_code = create_device(new_device_id.strip(), config_dict)
                        
                        if success:
                            st.success(message)
                            st.session_state.show_add_form = False
                            # Refresh device list
                            st.rerun()
                        else:
                            st.error(message)
    
    # Search Box
    search_query = st.text_input("🔍 Search by Device ID", placeholder="Enter device ID...")
    
    # Filter devices based on search
    if search_query:
        filtered_df = devices_df[devices_df['DEVICE_ID'].str.contains(search_query, case=False, na=False)]
    else:
        filtered_df = devices_df
    
    # Add Edit buttons column
    filtered_df_display = filtered_df.copy()
    
    # Display device table
    st.markdown("**Device List**")
    
    # Table header
    header_cols = st.columns([3, 3, 2, 3, 1, 1])
    with header_cols[0]:
        st.markdown("**Device ID**")
    with header_cols[1]:
        st.markdown("**Last Active**")
    with header_cols[2]:
        st.markdown("**Status**")
    with header_cols[3]:
        st.markdown("**Location**")
    with header_cols[4]:
        st.markdown("**View**")
    with header_cols[5]:
        st.markdown("**Edit**")
    
    st.markdown("---")
    
    # Initialize session state for editing
    if 'editing_device_id' not in st.session_state:
        st.session_state.editing_device_id = None
    
    # Create columns for table and edit buttons
    for idx, row in filtered_df_display.iterrows():
        device_id = row['DEVICE_ID']
        
        cols = st.columns([3, 3, 2, 3, 1, 1])
        
        with cols[0]:
            st.text(device_id)
        with cols[1]:
            st.text(row['LAST_ACTIVE'])
        with cols[2]:
            status_color = "🟢" if row['STATUS'] == "Active" else "🔴"
            st.text(f"{status_color} {row['STATUS']}")
        with cols[3]:
            st.text(row['LOCATION'])
        with cols[4]:
            if st.button("📊", key=f"view_{device_id}"):
                st.query_params.update(page="device", device_id=device_id)
                st.rerun()
        with cols[5]:
            if st.button("✏️", key=f"edit_{device_id}"):
                st.session_state.editing_device_id = device_id
                st.rerun()
        
        # Show edit form if this device is being edited
        if st.session_state.editing_device_id == device_id:
            with st.expander("Edit Device Configuration", expanded=True):
                # Fetch current configuration
                success, config, message = fetch_device_config(device_id)
                
                if not success:
                    st.error(message)
                else:
                    import json
                    formatted_config = json.dumps(config, indent=2)
                    
                    with st.form(key=f"edit_form_{device_id}"):
                        st.text_input("Device ID", value=device_id, disabled=True)
                        
                        config_text = st.text_area(
                            "Configuration (JSON) *",
                            value=formatted_config,
                            height=150,
                            help="Edit device configuration as valid JSON"
                        )
                        
                        col_submit, col_cancel = st.columns([1, 1])
                        
                        with col_submit:
                            submit_button = st.form_submit_button("Save Changes", type="primary")
                        
                        with col_cancel:
                            cancel_button = st.form_submit_button("Cancel")
                        
                        if cancel_button:
                            st.session_state.editing_device_id = None
                            st.rerun()
                        
                        if submit_button:
                            # Validation
                            errors = []
                            
                            # Check if configuration is empty
                            if not config_text or not config_text.strip():
                                errors.append("Configuration is required")
                            
                            # Validate JSON
                            config_dict = None
                            if config_text and config_text.strip():
                                try:
                                    config_dict = json.loads(config_text)
                                except json.JSONDecodeError as e:
                                    errors.append(f"Invalid JSON: {str(e)}")
                            
                            # Display errors or update device
                            if errors:
                                for error in errors:
                                    st.error(error)
                            else:
                                # Update device via API
                                with st.spinner("Updating device..."):
                                    success, message, status_code = update_device_config(device_id, config_dict)
                                
                                if success:
                                    st.success(message)
                                    st.session_state.editing_device_id = None
                                    # Refresh device list
                                    st.rerun()
                                else:
                                    st.error(message)
                    
                    # Delete button outside form
                    st.markdown("---")
                    
                    # Delete modal function
                    @st.dialog("Delete Device")
                    def delete_device_modal(device_id):
                        st.warning("⚠️ Are you sure you want to delete this device?")
                        st.markdown(f"**Device ID:** `{device_id}`")
                        st.markdown("This action **cannot be undone**.")
                        
                        col1, col2 = st.columns([1, 1])
                        
                        with col1:
                            if st.button("🗑️ Delete", key=f"modal_confirm_{device_id}", type="primary"):
                                # Execute delete
                                with st.spinner("Deleting device..."):
                                    success, message, status_code = delete_device(device_id)
                                
                                if success:
                                    st.success(message)
                                    st.session_state.editing_device_id = None
                                    # Wait a moment for user to see success message
                                    import time
                                    time.sleep(0.5)
                                    st.rerun()
                                else:
                                    st.error(message)
                        
                        with col2:
                            if st.button("Cancel", key=f"modal_cancel_{device_id}"):
                                st.rerun()
                    
                    # Delete button to open modal
                    if st.button("🗑️ Delete Device", key=f"delete_{device_id}"):
                        delete_device_modal(device_id)