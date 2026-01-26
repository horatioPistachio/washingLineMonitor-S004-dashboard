# AI Agent Guidelines

This document provides guidelines for AI agents working on the washingLineMonitor-S004-dashboard project.

## Project Overview

- **Purpose**: Internal IoT Fleet Manager dashboard for monitoring washing line sensors
- **Framework**: Streamlit (Python)
- **Backend**: Connects to washingLineMonitor-S003-webserver API
- **Priority**: Quick development, easy extensibility, internal use only

## Architecture Principles

### Keep It Simple
- This is an internal tool—prioritize speed of development over polish
- Use Streamlit's built-in components wherever possible
- Avoid over-engineering; add complexity only when necessary

### Single File Structure
- The main application lives in `app.py`
- Keep all dashboard logic in this single file unless it becomes unmanageable (500+ lines of a single concern)
- Only split into modules when there's a clear separation of concerns (e.g., API clients, data models)

### Extensibility Pattern
When adding new features:
1. Add new page options to the sidebar radio button in the `SIDEBAR` section
2. Create a new section in the main content area using conditional logic based on `menu_selection`
3. Follow the existing pattern: fetch data → display with Streamlit components

## Code Organization

```
app.py
├── Imports & Configuration
├── Custom CSS (st.markdown with <style>)
├── API Integration Functions (fetch_*)
├── Sidebar Navigation
└── Main Content (conditional based on menu_selection)
```

## Development Guidelines

### Adding New Pages
```python
# 1. Add to sidebar radio options
menu_selection = st.radio(
    "Navigation",
    ["Dashboard", "Devices", "New Page"],  # Add here
    ...
)

# 2. Add conditional section in main content
if menu_selection == "New Page":
    st.header("New Page Title")
    # Page content here
```

### Adding New API Integrations
```python
def fetch_new_data():
    """
    Brief description of what this fetches.
    """
    endpoint = os.environ.get('API_ENDPOINT', 'http://127.0.0.1:8000/')
    url = f"{endpoint}/api/v1/your-endpoint"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
    
    # Return sensible default on failure
    return []
```

### Styling
- Use the existing CSS in the `<style>` block for consistency
- Primary color: `#2176FF`
- Keep the compact, professional look
- Use `st.columns()` for layout

### Environment Variables
- Store all configuration in `.env` file
- Use `os.environ.get('VAR_NAME', 'default')` pattern
- Document new variables in README.md

## API Endpoints

The dashboard connects to the S003 webserver. Common endpoints:
- `GET /api/v1/devices` - List all devices
- `GET /api/v1/devices/{id}` - Device configuration
- `GET /api/v1/telemetry/{id}` - Device telemetry data

## External Services

- **Weather**: Open-Meteo API (free, no auth required)
- **Notifications**: ntfy.sh (topic-based, configured via `NTFY_TOPIC`)

## Testing

- Run with: `streamlit run app.py`
- Test API connectivity by checking console for error messages
- Verify environment variables are loaded correctly

## Common Tasks

### Add a new device status indicator
1. Fetch device data using existing `fetch_device_list()` or create new function
2. Display using `st.dataframe()` or `st.metric()`
3. Add status logic based on timestamps or API responses

### Add a new metric card
```python
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Metric Name", value, delta)
```

### Add a chart
```python
import streamlit as st
# Use st.line_chart(), st.bar_chart(), or st.altair_chart() for more control
st.line_chart(data)
```

## Do's and Don'ts

### Do
- Use Streamlit's caching (`@st.cache_data`) for expensive API calls
- Handle API failures gracefully with sensible defaults
- Keep the UI responsive with loading states
- Add print statements for debugging (internal tool)
- Follow existing code patterns

### Don't
- Over-engineer solutions
- Add authentication complexity (internal use)
- Create unnecessary abstractions
- Use external UI libraries unless absolutely necessary
- Break the single-page simplicity unless justified

## File Reference

| File | Purpose |
|------|---------|
| `app.py` | Main Streamlit application |
| `requirements.txt` | Python dependencies |
| `.env` | Environment configuration (not in git) |
| `.env.example` | Template for environment variables |
| `.prompts/` | AI prompt templates for features |
