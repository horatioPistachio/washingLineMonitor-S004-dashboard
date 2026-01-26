# System Statistics Integration

Replace the dummy system statistics on the Dashboard page with real metrics from a Glances monitoring service.

## Requirements

Integrate with Glances API to display real-time system statistics:
- **Disk Space Usage** - Total, used, and available disk space with percentage
- **Memory Usage** - Total, used, and available memory with percentage
- **CPU Load** - Current CPU utilization percentage

Include a link to the Glances web interface for detailed monitoring.

## API Endpoint

**GET** `http://localhost:61208/api/3/all`

**Response Format:** JSON object containing various system metrics

**Key Response Fields:**
```json
{
  "fs": [
    {
      "device_name": "C:\\",
      "fs_type": "NTFS",
      "mnt_point": "C:\\",
      "size": 536870912000,       // Total size in bytes
      "used": 402653184000,        // Used space in bytes
      "free": 134217728000,        // Free space in bytes
      "percent": 75.0              // Usage percentage
    }
  ],
  "mem": {
    "total": 17179869184,          // Total RAM in bytes
    "available": 8589934592,       // Available RAM in bytes
    "percent": 50.0,               // Usage percentage
    "used": 8589934592             // Used RAM in bytes
  },
  "cpu": {
    "total": 45.2,                 // Total CPU usage percentage
    "user": 30.5,                  // User CPU percentage
    "system": 14.7                 // System CPU percentage
  }
}
```

**Note:** Response structure may vary based on OS and Glances version. Handle missing fields gracefully.

## Implementation Notes

### Configuration
- Add `GLANCES_ENDPOINT` to `.env` file (default: `http://localhost:61208`)
- Use environment variable for endpoint configuration
- Add to `.env.example` for documentation

### Function to Create
Replace `fetch_system_metrics()` function with real implementation:
- Fetch data from Glances API endpoint `/api/3/all`
- Extract disk, memory, and CPU metrics
- Convert bytes to human-readable format (GB, MB)
- Handle errors gracefully with fallback values
- Return structured data matching existing format

### Data Extraction
**Disk Space:**
- Use first filesystem in `fs` array (usually primary drive)
- Extract: `size`, `used`, `free`, `percent`
- Convert bytes to GB: `bytes / (1024**3)`

**Memory:**
- Extract from `mem` object: `total`, `used`, `available`, `percent`
- Convert bytes to GB

**CPU:**
- Extract `total` from `cpu` object
- Display as percentage

### Display Requirements
Replace the existing "System State" section metrics with real data:

**Column 1 - Disk Space Usage:**
- Title: "Disk Space Usage"
- Display: `XX% of XXX GB`
- Progress bar showing percentage
- Change indicator: Not applicable (remove for real data)

**Column 2 - Memory Usage:**
- Title: "Memory Usage"
- Display: `XX% of XX GB`
- Progress bar showing percentage
- Optional: Show used/available below

**Column 3 - CPU Load:**
- Title: "CPU Load"
- Display: `XX%`
- Color coding:
  - Green: < 60%
  - Orange: 60-80%
  - Red: > 80%

**Link to Glances:**
Add below metrics or in sidebar:
```python
st.markdown(f"[📊 View Detailed System Stats]({glances_url})")
```

### Error Handling
- Network timeout: 5 seconds
- Connection errors: Display "--" for all metrics
- Missing fields: Use default values or "--"
- Invalid JSON: Log error and return defaults
- Print errors to console for debugging (internal tool)

### Fallback Behavior
If Glances is unavailable:
- Show all metrics as "--"
- Display info message: "System stats unavailable (Glances service not running)"
- Don't block dashboard loading

## Code Structure

```python
def fetch_system_metrics():
    """
    Fetch real-time system metrics from Glances API
    Returns dict with disk, memory, and CPU metrics
    """
    import os
    
    endpoint = os.environ.get('GLANCES_ENDPOINT', 'http://localhost:61208')
    url = f"{endpoint}/api/3/all"
    
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
```

## Display Example

```python
# System State Section
st.markdown("**System State**")

metrics = fetch_system_metrics()

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("<small>Disk Space Usage</small>", unsafe_allow_html=True)
    disk = metrics["disk"]
    if disk["total_gb"] > 0:
        st.markdown(f"### {disk['percentage']:.1f}% <small>of {disk['total_gb']:.0f} GB</small>", unsafe_allow_html=True)
        st.progress(disk['percentage'] / 100)
    else:
        st.markdown("### --")

with col2:
    st.markdown("<small>Memory Usage</small>", unsafe_allow_html=True)
    mem = metrics["memory"]
    if mem["total_gb"] > 0:
        st.markdown(f"### {mem['percentage']:.1f}% <small>of {mem['total_gb']:.1f} GB</small>", unsafe_allow_html=True)
        st.progress(mem['percentage'] / 100)
    else:
        st.markdown("### --")

with col3:
    st.markdown("<small>CPU Load</small>", unsafe_allow_html=True)
    cpu = metrics["cpu"]
    if cpu["percentage"] > 0:
        st.markdown(f"### {cpu['percentage']:.1f}%", unsafe_allow_html=True)
        # Color coding
        color = "green" if cpu["percentage"] < 60 else "orange" if cpu["percentage"] < 80 else "red"
        st.markdown(f"<small>:{color}[Current load]</small>", unsafe_allow_html=True)
    else:
        st.markdown("### --")

# Link to Glances
glances_url = os.environ.get('GLANCES_ENDPOINT', 'http://localhost:61208')
st.markdown(f"[📊 View Detailed System Stats]({glances_url})", unsafe_allow_html=True)
```

## Testing

- Ensure Glances is running: `http://localhost:61208`
- Test with Glances stopped to verify fallback behavior
- Verify metrics update in real-time (Streamlit auto-refresh)
- Check different OS compatibility (Windows/Linux path differences)