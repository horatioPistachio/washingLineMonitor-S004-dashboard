# Backend Data Pull Functions

Create Python functions to fetch data from the washing line monitor API.

---

## Configuration

**Base Endpoint**: `http://washinglinemonitor-s003-webserver-app`  
**API Version**: `v1`  
**Base URL**: `{endpoint}/api/v1`

Use the `requests` library for all HTTP calls. Include proper error handling (try/except blocks) for network errors and invalid responses.

---

## Function 1: `fetch_notifications()`

**Purpose**: Fetch the latest notifications from the ntfy.sh service.

**API Details**:
- Endpoint: `https://ntfy.sh/{topic}/json?poll=1&since=latest`
- Method: GET
- The topic should be configurable (environment variable or parameter)

**Implementation Requirements**:
- Use `requests.get()` to fetch notifications
- Parse JSON response
- Return list of notification objects
- Each notification contains: `id`, `time`, `event`, `topic`, `message`, `title`, `priority`

**Error Handling**:
- Handle connection errors
- Handle JSON parsing errors
- Return empty list on failure

---

## Function 2: `fetch_device_list()`

**Purpose**: Fetch a complete list of devices with their status, location, and last activity.

**Multi-Step Process**:

### Step 1: Get all device IDs
- **Endpoint**: `{endpoint}/api/v1/devices`
- **Method**: GET
- **Response Format**: 
  ```json
  [
    {"device_id": "device_001"},
    {"device_id": "device_002"}
  ]
  ```

### Step 2: For each device, fetch configuration
- **Endpoint**: `{endpoint}/api/v1/devices/{device_id}`
- **Method**: GET
- **Response Format**:
  ```json
  {
    "device_id": "device_001",
    "configuration": {
      "location": "Bedroom",
      // other configuration fields
    }
  }
  ```
- **Extract**: `location` from the `configuration` object

### Step 3: For each device, fetch telemetry data
- **Endpoint**: `{endpoint}/api/v1/telemetry/{device_id}`
- **Method**: GET
- **Optional Query Parameters**:
  - `start_time`: ISO format datetime (e.g., "2026-01-18T10:00:00")
  - `end_time`: ISO format datetime
- **Response Format**:
  ```json
  [
    {
      "device_id": "device_001",
      "payload": {"temp": 23.5, "humidity": 60},
      "timestamp": "2026-01-18T14:30:00Z"
    }
  ]
  ```
- **Note**: Results are ordered by timestamp DESC (newest first)
- **Extract**: Latest `timestamp` (first item in array) for `last_active`

### Step 4: Determine device status
- **Status Logic**:
  - If telemetry data is empty: `"Unknown"`
  - If latest timestamp is within last 1 hour: `"Active"`
  - Otherwise: `"Inactive"`
- Use `datetime` module to compare timestamps with current time

**Return Format**:
Return a list of dictionaries, each containing:
```python
{
    "device_id": str,
    "location": str,
    "last_active": str (ISO format datetime),
    "status": str ("Active" | "Inactive" | "Unknown")
}
```

**Performance Considerations**:
- Consider using concurrent requests (e.g., `asyncio` or `ThreadPoolExecutor`) for fetching individual device details
- Implement caching if this function is called frequently

**Error Handling**:
- Handle 404 errors (device not found)
- Skip devices that fail to fetch and continue with others
- Log errors for debugging

---

## Function 3: `fetch_device_count()`

**Purpose**: Get the total number of registered devices.

**API Details**:
- **Endpoint**: `{endpoint}/api/v1/devices`
- **Method**: GET
- **Response Format**: Array of device objects

**Implementation**:
- Fetch the devices list
- Return `len(devices)` as the count
- Return `0` on error

**Optimization Note**: 
This could be optimized by reusing the result from `fetch_device_list()` if both functions are called together, rather than making duplicate API calls.

---

## Additional Implementation Notes

1. **Configuration Management**:
   - Store the base endpoint URL in an environment variable or config file
   - Store the ntfy.sh topic in configuration

2. **Timestamp Handling**:
   - Use `datetime.datetime.fromisoformat()` to parse timestamps
   - Use `datetime.datetime.utcnow()` for current time comparison
   - Handle timezone-aware datetimes (UTC)

3. **HTTP Best Practices**:
   - Set reasonable timeouts (e.g., 10 seconds)
   - Add retry logic for transient failures
   - Use session objects for connection pooling

4. **Testing**:
   - Mock the API responses for unit testing
   - Test edge cases (empty device list, missing location, no telemetry data)

5. **Logging**:
   - Log API calls and responses for debugging
   - Log any errors or unexpected responses

