I would like to create a device management page for the IoT Fleet Manager dashboard. The device management page will be displayed when the "Devices" radio button is selected in the sidebar navigation.

## Requirements

### Page Structure
The device management page should be conditionally displayed when `menu_selection == "Devices"`. When the "Dashboard" option is selected, show the existing dashboard content.

### API Integration Functions
Create a new function `fetch_device_list()` that returns a DataFrame with placeholder data for at least 12 devices. The DataFrame should include:
- `DEVICE_ID`: Device identifier (e.g., "IOT-B01", "IOT-B02", etc.)
- `LAST_ACTIVE`: Timestamp in format "YYYY-MM-DD HH:MM:SS"
- `STATUS`: Either "Active" or "Inactive" (use "Active" for devices with recent timestamps within last 24 hours, "Inactive" for older timestamps)
- `LOCATION`: Placeholder location names

### Device Summary Metrics Section
Display 2 columns at the top showing:
1. **Total Devices**: Total count of devices
2. **Active Devices**: Count of devices with status "Active"

Use the same styling pattern as the existing "System State" metrics section with:
- `<small>` tags for labels
- `###` markdown for large numbers
- Green/red color indicators where appropriate

### Device Table
Display the device list using `st.dataframe()` with the following specifications:
- Set `width='stretch'` for full width
- Set `hide_index=True`
- Add a search box above the table using `st.text_input()` to filter devices by Device ID
- The table should display all columns from the DataFrame
- Set an appropriate height (e.g., 400px)

### Action Buttons
Add two buttons:
1. **Add New Device** button (using `st.button()`) - positioned above the table
2. **Edit device** button at the end of each row in the device table.

### Styling Guidelines
- Use Streamlit's built-in components and styling
- Follow the existing pattern with `st.markdown("### Section Title")` for headers
- Use `st.markdown("---")` for horizontal dividers where appropriate
- Maintain consistency with the existing dashboard's compact spacing and layout
- Use the existing color scheme (blue gradient header for the main weather section is already in place)
