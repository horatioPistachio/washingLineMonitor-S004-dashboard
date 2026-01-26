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

def fetch_weather_data():
    """
    Fetch weather data from API
    TODO: Implement API call to weather service
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

def fetch_notifications():
    """
    Fetch recent notifications from ntfy.sh API
    Returns a DataFrame with TIMESTAMP, TITLE, MESSAGE, DEVICE ID columns
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

def fetch_system_metrics():
    """
    Fetch system state metrics from API
    TODO: Implement API call to metrics service
    """
    # Placeholder data
    return {
        "db_space_usage": {
            "percentage": 67,
            "total_gb": 500,
            "change_from_avg": -8,
            "change_type": "decrease"
        },
        "device_data_rate": {
            "value": 2.4,
            "unit": "MB/s",
            "change_from_avg": 8,
            "change_type": "increase"
        },
        "avg_request_time": {
            "value": 124,
            "unit": "ms",
            "change_from_last_week": -12,
            "change_type": "decrease"
        }
    }

def fetch_device_count():
    """
    Fetch total device count from API
    Returns the number of registered devices
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

def fetch_device_list():
    """
    Fetch device list from API with complete information
    Combines data from /devices, /devices/{id}, and /telemetry/{id} endpoints
    Returns a DataFrame with DEVICE_ID, LOCATION, LAST_ACTIVE, STATUS columns
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

with st.sidebar:
    st.title("📡 IoT Fleet Manager")
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
    device_count = fetch_device_count()  # API call placeholder
    st.markdown(f"### Total Devices")
    st.markdown(f"# {device_count}")

# ============================================================================
# MAIN CONTENT
# ============================================================================

if menu_selection == "Dashboard":
    # Weather Header
    weather_data = fetch_weather_data()  # API call placeholder

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

    # Fetch metrics data
    metrics = fetch_system_metrics()  # API call placeholder

    # Create 3 columns for metrics
    col1, col2, col3 = st.columns(3)

    # Metric 1: DB Space Usage
    with col1:
        st.markdown("<small>DB Space Usage</small>", unsafe_allow_html=True)
        db_metrics = metrics["db_space_usage"]
        st.markdown(f"### {db_metrics['percentage']}% <small>of {db_metrics['total_gb']} GB</small>", unsafe_allow_html=True)
        st.progress(db_metrics['percentage'] / 100)
        
        change_color = "green" if db_metrics['change_type'] == "decrease" else "red"
        change_arrow = "↓" if db_metrics['change_type'] == "decrease" else "↑"
        st.markdown(f"<small>:{change_color}[{change_arrow} {abs(db_metrics['change_from_avg'])}% from average]</small>", unsafe_allow_html=True)

    # Metric 2: Device Data Rate
    with col2:
        st.markdown("<small>Device Data Rate</small>", unsafe_allow_html=True)
        rate_metrics = metrics["device_data_rate"]
        st.markdown(f"### {rate_metrics['value']} {rate_metrics['unit']}", unsafe_allow_html=True)
        
        change_color = "green" if rate_metrics['change_type'] == "increase" else "red"
        change_arrow = "↑" if rate_metrics['change_type'] == "increase" else "↓"
        st.markdown(f"<small>:{change_color}[{change_arrow} {abs(rate_metrics['change_from_avg'])}% from average]</small>", unsafe_allow_html=True)

    # Metric 3: Average Request Time
    with col3:
        st.markdown("<small>Average Request Time</small>", unsafe_allow_html=True)
        time_metrics = metrics["avg_request_time"]
        st.markdown(f"### {time_metrics['value']} {time_metrics['unit']}", unsafe_allow_html=True)
        
        change_color = "green" if time_metrics['change_type'] == "decrease" else "red"
        change_arrow = "↓" if time_metrics['change_type'] == "decrease" else "↑"
        st.markdown(f"<small>:{change_color}[{change_arrow} {abs(time_metrics['change_from_last_week'])}ms from last week]</small>", unsafe_allow_html=True)

elif menu_selection == "Devices":
    # Device Management Page
    st.markdown("### Device Management")
    st.markdown("---")
    
    # Fetch device data
    devices_df = fetch_device_list()  # API call placeholder
    
    # Device Summary Metrics
    total_devices = len(devices_df)
    active_devices = len(devices_df[devices_df['STATUS'] == 'Active'])
    
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
    header_cols = st.columns([3, 3, 2, 3, 1])
    with header_cols[0]:
        st.markdown("**Device ID**")
    with header_cols[1]:
        st.markdown("**Last Active**")
    with header_cols[2]:
        st.markdown("**Status**")
    with header_cols[3]:
        st.markdown("**Location**")
    with header_cols[4]:
        st.markdown("**Actions**")
    
    st.markdown("---")
    
    # Create columns for table and edit buttons
    for idx, row in filtered_df_display.iterrows():
        cols = st.columns([3, 3, 2, 3, 1])
        
        with cols[0]:
            st.text(row['DEVICE_ID'])
        with cols[1]:
            st.text(row['LAST_ACTIVE'])
        with cols[2]:
            status_color = "🟢" if row['STATUS'] == "Active" else "🔴"
            st.text(f"{status_color} {row['STATUS']}")
        with cols[3]:
            st.text(row['LOCATION'])
        with cols[4]:
            if st.button("✏️", key=f"edit_{row['DEVICE_ID']}"):
                st.info(f"Edit functionality for {row['DEVICE_ID']} will be implemented in future release.")