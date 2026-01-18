# IoT Fleet Manager Dashboard - Skeleton Generator

## Overview
Please generate a complete Streamlit dashboard skeleton based on the reference image (dashboard_image.png). This dashboard will be for an IoT Fleet Manager application that monitors and manages IoT devices.

## Requirements

### Technology Stack
- **Framework**: Streamlit
- **Data Source**: API (to be integrated later)
- **Styling**: Use Streamlit's native components and custom CSS where necessary however lean on Streamlit's built-in styling as much as possible.

### Dashboard Structure

#### 1. **Header Section**
- Blue gradient background (#2176FF or similar)
- Display weather widget showing:
  - Temperature (with sun/cloud icon)
  - Weather description (e.g., "Partly Cloudy")
  - Wind speed (with icon)
  - Precipitation percentage (with icon)
  - Humidity percentage (with icon)
  - Location display (aligned right)
- Use placeholder data/functions for weather information

#### 2. **Sidebar Navigation**
- Title: "IoT Fleet Manager"
- Subtitle: "Device Management"
- Navigation menu items:
  - Dashboard (selected/highlighted)
  - Devices
- Display total device count at the bottom (e.g., "Total Devices: 247")
- Use placeholder data for device count

#### 3. **Main Content Area**

##### Recent Notifications Table
- Section title: "Recent Notifications"
- Four columns: TIMESTAMP | TITLE | MESSAGE | DEVICE ID
- Include 5 sample notification rows with placeholder data
- Use a clean, bordered table layout
- Column headers should be uppercase and muted gray

##### System State Metrics (3-column layout)
- Section title: "System State"

**Metric 1: DB Space Usage**
- Display percentage value (e.g., "67%")
- Show capacity (e.g., "of 500 GB")
- Include progress bar visualization
- Show comparison text (e.g., "↓ 8% from average") with appropriate color (green for decrease)

**Metric 2: Device Data Rate**
- Display rate value (e.g., "2.4 MB/s")
- Show comparison text (e.g., "↑ 8% from average") with appropriate color (green for increase)

**Metric 3: Average Request Time**
- Display time value (e.g., "124 ms")
- Show comparison text (e.g., "↓ 12ms from last week") with appropriate color (green for decrease)

#### 4. **Right Sidebar** (Optional/Stretch Goal)
- Display notification indicators with icons:
  - Error icon with timestamp
  - Message icon with timestamp
  - Warning icon with timestamp
  - etc.

## Implementation Guidelines

1. **Leave Functions Empty**: Create function stubs (with `pass` or placeholder comments) for:
   - `fetch_weather_data()`
   - `fetch_notifications()`
   - `fetch_system_metrics()`
   - `fetch_device_count()`
   
2. **Use Placeholder Data**: For now, use static/hardcoded sample data in variables that can be easily replaced later

3. **Styling**: Stick to steamlit's built-in styling as much as possible.

4. **Layout**: Use Streamlit's layout components:
   - `st.sidebar` for navigation
   - `st.columns()` for multi-column layouts
   - `st.container()` for sections
   - `st.markdown()` for custom styling

5. **Comments**: Add clear comments indicating where API integration should occur

6. **Responsiveness**: Structure should be clean and responsive

## Deliverables
- Complete `app.py` file with full dashboard skeleton
- All UI components visible and properly styled
- Clear placeholder sections marked for API integration
- Runnable application (even with static data)

## Notes
- The current app.py only contains "Hello world" - please replace entirely with the dashboard skeleton
- Focus on layout and structure; actual data fetching will be implemented later
- Ensure the color scheme matches the blue theme shown in the reference image

