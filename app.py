import streamlit as st
import pandas as pd
from datetime import datetime

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
    # Placeholder data
    return {
        "temperature": 24,
        "condition": "Partly Cloudy",
        "wind_speed": 12,
        "precipitation": 20,
        "humidity": 65,
        "location": "San Francisco, CA"
    }

def fetch_notifications():
    """
    Fetch recent notifications from API
    TODO: Implement API call to notification service
    """
    # Placeholder data
    return pd.DataFrame({
        "TIMESTAMP": [
            "2026-01-18 14:32:15",
            "2026-01-18 14:28:33",
            "2026-01-18 14:25:12",
            "2026-01-18 14:15:47",
            "2026-01-18 14:08:22"
        ],
        "TITLE": [
            "Temperature Alert",
            "Connection Lost",
            "Vibration Alert",
            "Motion Detected",
            "System Update"
        ],
        "MESSAGE": [
            "High temperature detected",
            "Device went offline",
            "High vibration detected",
            "Unusual activity detected",
            "Firmware updated successfully"
        ],
        "DEVICE ID": [
            "IOT-B01",
            "IOT-B05",
            "IOT-B09",
            "IOT-B03",
            "IOT-B02"
        ]
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
    TODO: Implement API call to device service
    """
    # Placeholder data
    return 247

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