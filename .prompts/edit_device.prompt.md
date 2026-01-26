# Edit Device Configuration Functionality

Add functionality to edit existing device configurations and delete devices in the Streamlit dashboard.

## Requirements

When a user clicks the pencil (✏️) button in the device list:
1. Open a form (use `st.expander()` or conditional rendering similar to "Add Device")
2. Pre-populate the form with existing device data:
   - **Device ID** (text input, **read-only/disabled**)
   - **Configuration** (text area with current JSON, editable)
3. Include a "Delete Device" button at the bottom of the form (styled as danger/warning)

On form submission:
1. Validate that Configuration is not empty
2. Validate that Configuration is valid JSON
3. Send PATCH request to update the device configuration
4. Display success/error message to user
5. Clear/close form on success
6. Refresh device list to show updated data

### Delete Device - Two-Step Confirmation

When user clicks "Delete Device" button:
1. **First click**: Show confirmation message with warning (e.g., using `st.warning()`)
   - Display: "⚠️ Are you sure? Click 'Confirm Delete' again to permanently delete this device."
   - Change button to "Confirm Delete" with red/danger styling
   - Track confirmation state in session state (e.g., `st.session_state.delete_confirm_{device_id}`)
2. **Second click**: Execute the delete operation
   - Send DELETE request to API
   - Display success/error message
   - Clear form and refresh device list on success
   - Reset confirmation state

If user cancels or clicks away, reset the confirmation state.

## API Endpoints

### Update Device Configuration

**PATCH** `/api/v1/devices/{device_id}`

**Request Body:**
```json
{
  "device_id": "string",  // Must match the device_id in URL path
  "configuration": {}     // JSON object - the updated configuration
}
```

**Response Codes:**
- `200 OK` - Device configuration updated successfully
- `404 Not Found` - Device with this ID does not exist
- `400 Bad Request` - Invalid request format
- `500 Internal Server Error` - Database or server error

### Delete Device

**DELETE** `/api/v1/devices/{device_id}`

**Request Body:** None required

**Response Codes:**
- `204 No Content` - Device deleted successfully
- `404 Not Found` - Device with this ID does not exist
- `500 Internal Server Error` - Database or server error

## Implementation Notes

- Follow the existing "Add Device" pattern for consistency:
  - Use session state to track which device is being edited (e.g., `st.session_state.editing_device_id`)
  - Use similar form structure with `st.form()`
  - Reuse validation logic from add device
  
- Create a new function `fetch_device_config(device_id)` to retrieve current configuration:
  - Use `GET /api/v1/devices/{device_id}` endpoint
  - Extract the `configuration` field from response
  - Convert to formatted JSON string for display in text area
  
- Create a new function `update_device_config(device_id, configuration)`:
  - Use `requests.patch()` with the endpoint from environment variable
  - Return tuple: (success: bool, message: str, status_code: int)

- Create a new function `delete_device(device_id)`:
  - Use `requests.delete()` with the endpoint from environment variable
  - Return tuple: (success: bool, message: str, status_code: int)
  - Handle 204 (success), 404 (not found), and network errors
  
- UI/UX considerations:
  - When pencil button clicked, set `st.session_state.editing_device_id` to that device's ID
  - Show form only for the device being edited (check if `editing_device_id` matches)
  - Display Device ID in a disabled/read-only text input (use `disabled=True`)
  - Pre-populate configuration text area with nicely formatted JSON (use `json.dumps(config, indent=2)`)
  - Include "Save Changes" and "Cancel" buttons
  - Include "Delete Device" button below the form (outside the form to avoid form submission conflict)
  - Use session state to track delete confirmation: `st.session_state.delete_confirm_{device_id}`
  - Clear `editing_device_id` from session state on cancel or success
  - Use `st.rerun()` to refresh after successful update or delete
  
- Delete button behavior:
  - Initially shows as "🗑️ Delete Device" (no special styling on first click)
  - On first click: Show warning message and change button to "⚠️ Confirm Delete"
  - On second click: Execute deletion
  - Reset confirmation state if user cancels edit form or clicks another device
  - Use different button key for confirmed state to allow re-rendering
  
- Validation:
  - Validate JSON syntax before submission
  - Alert user if invalid JSON with specific error message
  - Show error feedback using `st.error()`
  - Show success feedback using `st.success()`
  
- Error handling:
  - Handle 404 errors (device not found) for both update and delete
  - Handle 204 response for successful deletion
  - Handle network errors gracefully
  - Display meaningful error messages to user
  - Show warning before destructive delete operation

## Form Structure Example

```python
if st.session_state.get('editing_device_id') == row['DEVICE_ID']:
    with st.expander("Edit Device Configuration", expanded=True):
        with st.form(key=f"edit_form_{row['DEVICE_ID']}"):
            st.text_input("Device ID", value=device_id, disabled=True)
            config_text = st.text_area("Configuration (JSON)", value=formatted_json, height=150)
            
            col1, col2 = st.columns([1, 1])
            with col1:
                submit = st.form_submit_button("Save Changes", type="primary")
            with col2:
                cancel = st.form_submit_button("Cancel")
        
        # Delete button outside form (to avoid form submission conflict)
        st.markdown("---")
        
        # Check if delete confirmation is active
        delete_confirm_key = f"delete_confirm_{device_id}"
        if st.session_state.get(delete_confirm_key, False):
            st.warning("⚠️ Are you sure? This action cannot be undone!")
            if st.button("⚠️ Confirm Delete", key=f"confirm_delete_{device_id}", type="secondary"):
                # Execute delete
                success, message, status = delete_device(device_id)
                # Handle result...
        else:
            if st.button("🗑️ Delete Device", key=f"delete_{device_id}"):
                st.session_state[delete_confirm_key] = True
                st.rerun()
```