# Add Device Functionality

Add functionality to the "Add Device" button in the Streamlit dashboard.

## Requirements

When clicked, the button should reveal a form (use `st.expander()` or conditional rendering) that allows the user to input:
- **Device ID** (text input, required)
- **Configuration** (text area for JSON input, required)

On form submission:
1. Validate that Device ID is not empty
2. Validate that Configuration is valid JSON
3. Send POST request to create the device
4. Display success/error message to user
5. Clear form on success

## API Endpoint

**POST** `/api/v1/devices`

**Request Body:**
```json
{
  "device_id": "string",
  "configuration": {} // JSON object
}
```

**Response Codes:**
- `201 Created` - Device created successfully
- `409 Conflict` - Device with this ID already exists
- `400 Bad Request` - Invalid request format

## Implementation Notes

- Follow the existing pattern in app.py for API calls using `fetch_*` function naming
- Use `requests.post()` with the endpoint from environment variable
- Add error handling for network errors and API responses
- Display feedback using `st.success()` or `st.error()`
- Consider adding a refresh button or auto-refresh device list after successful creation
- Valid the Json before submission, Alert user if invalid.