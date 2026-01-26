# Device Telemetry Visualization

Add dedicated device pages with time-series plots for telemetry data visualization and algorithm improvement.

## Requirements

### Navigation
When a user clicks on a device row in the "Devices" page:
1. Navigate to a dedicated device page
2. Use Streamlit query parameters to specify the device: `?page=device&device_id=test0001`
3. Update the navigation menu to show a "← Back to Devices" option when viewing a device

### Device Page Features
- Time-series plots for all telemetry metrics
- Time range selector (1h, 6h, 12h, 24h, 7d, 30d)
- Device header with key information
- CSV download functionality
- Real-time data updates

## API Endpoint

**GET** `/api/v1/telemetry/{device_id}`

**Query Parameters:**
- `start_time` (optional): ISO format datetime string (e.g., "2026-01-18T06:12:01")
- `end_time` (optional): ISO format datetime string
- If omitted, returns all telemetry data (default behavior from API)

**Response Format:**
```json
[
  {
    "device_id": "test0001",
    "payload": {
      "resistance": 25000,
      "temperature": 22.5,
      "humidity": 65.0
    },
    "timestamp": "2026-01-18T06:12:01.876599Z"
  },
  {
    "device_id": "test0001",
    "payload": {
      "resistance": 24800,
      "temperature": 22.7,
      "humidity": 64.5
    },
    "timestamp": "2026-01-18T06:17:01.123456Z"
  }
]
```

**Notes:**
- Timestamps are in ISO 8601 format with UTC timezone (Z suffix)
- Payload is a JSON object with variable keys depending on device type
- Each device may have different metrics in their payload
- Response is ordered by timestamp (typically DESC from API)

## Implementation

### 1. URL Routing with Query Parameters

Streamlit doesn't support traditional URL routing, but uses query parameters:

```python
# Get query parameters
query_params = st.query_params

# Check if we're viewing a device page
if query_params.get("page") == "device" and query_params.get("device_id"):
    device_id = query_params.get("device_id")
    # Show device page
else:
    # Show normal navigation
```

### 2. Navigation from Device List

Modify the device list table to make rows clickable:

```python
# In the device list loop
if st.button(f"📊", key=f"view_{device_id}"):
    st.query_params.update(page="device", device_id=device_id)
    st.rerun()
```

Or make entire row clickable using a button:
```python
with cols[0]:
    if st.button(device_id, key=f"view_{device_id}", use_container_width=True):
        st.query_params.update(page="device", device_id=device_id)
        st.rerun()
```

### 3. Fetch Telemetry Function

Create a new function to fetch telemetry data with time range:

```python
def fetch_telemetry_data(device_id, start_time=None, end_time=None):
    """
    Fetch telemetry data for a device within a time range
    
    Args:
        device_id: Device identifier
        start_time: datetime object for range start (optional)
        end_time: datetime object for range end (optional)
    
    Returns:
        tuple: (success: bool, data: list, message: str)
    """
    import os
    from datetime import datetime
    
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
```

### 4. Time Range Calculation

```python
from datetime import datetime, timedelta

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
```

### 5. Data Processing

Convert timestamps to local time and extract metrics:

```python
import pandas as pd
from datetime import datetime

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
```

### 6. Plotting with Streamlit

Use Streamlit's native charting or Plotly for interactive plots:

```python
import streamlit as st

# Get metric columns (all except timestamp)
metric_columns = [col for col in df.columns if col != 'timestamp']

if not metric_columns:
    st.warning("No metrics found in telemetry data")
else:
    # Create one plot per metric
    for metric in metric_columns:
        st.markdown(f"### {metric.replace('_', ' ').title()}")
        
        # Prepare data for plotting
        plot_df = df[['timestamp', metric]].copy()
        plot_df = plot_df.set_index('timestamp')
        
        # Use Streamlit line chart
        st.line_chart(plot_df, use_container_width=True)
        
        # Or use Plotly for more control:
        # import plotly.express as px
        # fig = px.line(df, x='timestamp', y=metric, markers=True,
        #               title=f"{metric.replace('_', ' ').title()}")
        # st.plotly_chart(fig, use_container_width=True)
```

### 7. CSV Download

```python
import io

def convert_df_to_csv(df):
    """Convert DataFrame to CSV for download"""
    return df.to_csv(index=False).encode('utf-8')

# Download button
if not df.empty:
    csv_data = convert_df_to_csv(df)
    st.download_button(
        label="📥 Download CSV",
        data=csv_data,
        file_name=f"{device_id}_telemetry_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        type="primary"
    )
```

## Page Layout Structure

```python
# Device page header
st.markdown(f"### Device {device_id}")

# Fetch device config for location
success, config, message = fetch_device_config(device_id)
location = config.get('location', 'Unknown') if success else 'Unknown'

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
    # Get from most recent telemetry timestamp
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

# Controls row
col_range, col_download = st.columns([3, 1])

with col_range:
    selected_range = st.selectbox("Time Range", list(time_ranges.keys()))

with col_download:
    st.markdown("<br>", unsafe_allow_html=True)  # Align button
    if not df.empty:
        csv_data = convert_df_to_csv(df)
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name=f"{device_id}_telemetry.csv",
            mime="text/csv"
        )

st.markdown("---")

# Plots section
if df.empty:
    st.info("No telemetry data available for the selected time range.")
else:
    st.markdown("**Telemetry Data**")
    
    metric_columns = [col for col in df.columns if col != 'timestamp']
    
    for metric in metric_columns:
        st.markdown(f"#### {metric.replace('_', ' ').title()}")
        plot_df = df[['timestamp', metric]].copy().set_index('timestamp')
        st.line_chart(plot_df, use_container_width=True)
```

## Navigation Back to Devices

Add a back button at the top of the device page:

```python
if st.button("← Back to Devices"):
    st.query_params.clear()
    st.rerun()
```

Or update the sidebar to show current context:

```python
with st.sidebar:
    st.title("📡 IoT Fleet Manager")
    
    # Check if viewing device page
    query_params = st.query_params
    if query_params.get("page") == "device":
        st.markdown("**Viewing Device Details**")
        if st.button("← Back to Dashboard"):
            st.query_params.clear()
            st.rerun()
    else:
        st.markdown("**Device Management**")
        # Normal navigation...
```

## Error Handling

- Handle missing device gracefully (404 from API)
- Handle no data in time range
- Handle malformed payload data
- Display user-friendly error messages
- Fall back to empty charts with informative messages

## Performance Considerations

- Cache telemetry data for short periods (30s) using `@st.cache_data`
- Limit data points for long time ranges (consider downsampling)
- Show loading spinners during data fetch
- Handle large datasets efficiently (thousands of points)

## Testing Checklist

- [ ] Navigate from device list to device page
- [ ] Back navigation works correctly
- [ ] All time ranges fetch correct data
- [ ] Timestamps display in local timezone
- [ ] All metrics from payload are plotted
- [ ] CSV download includes all data
- [ ] Empty data states show appropriate messages
- [ ] Device not found errors are handled
- [ ] Multiple metrics display correctly
- [ ] Page works for devices with different payload structures




