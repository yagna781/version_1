import requests
from requests.auth import HTTPBasicAuth
import json
import threading
import time

# Grafana details
GRAFANA_URL = "http://localhost:3000"
USERNAME = "admin"         # Replace with your Grafana username
PASSWORD = "yagna781"         # Replace with your Grafana password
DASHBOARD_TITLE = "Simple Dashboard with Empty Text Panel"  # Dashboard title created earlier

headers = {
    "Content-Type": "application/json"
}


def get_dashboard_uid():
    """Fetch the UID of the dashboard based on its title."""
    response = requests.get(
        f"{GRAFANA_URL}/api/search?query={DASHBOARD_TITLE}",
        auth=HTTPBasicAuth(USERNAME, PASSWORD)
    )
    if response.status_code == 200:
        dashboards = response.json()
        if dashboards:
            return dashboards[0]['uid']
    print("Dashboard not found!")
    return None


def get_dashboard(uid):
    """Fetch the existing dashboard configuration using UID."""
    response = requests.get(
        f"{GRAFANA_URL}/api/dashboards/uid/{uid}",
        auth=HTTPBasicAuth(USERNAME, PASSWORD)
    )
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch dashboard: {response.status_code} - {response.text}")
        return None


def update_text_panel(dashboard, new_text):
    """Update the text panel with new content."""
    panels = dashboard['dashboard']['panels']
    for panel in panels:
        if panel['type'] == 'text':
            panel['options']['content'] = new_text  # Update text content
    return dashboard


def push_dashboard(updated_dashboard):
    """Push the updated dashboard back to Grafana."""
    payload = {
        "dashboard": updated_dashboard['dashboard'],
        "overwrite": True
    }
    response = requests.post(
        f"{GRAFANA_URL}/api/dashboards/db",
        headers=headers,
        auth=HTTPBasicAuth(USERNAME, PASSWORD),
        data=json.dumps(payload)
    )
    if response.status_code == 200:
        print("Dashboard updated successfully!")
    else:
        print(f"Failed to update dashboard: {response.status_code} - {response.text}")


def command_line_input(uid):
    """Continuously listen for user input from the command line and update Grafana."""
    print("Type your message below. Type 'exit' to stop the script.")
    while True:
        user_input = input("Enter text for Grafana panel: ")
        if user_input.lower() == 'exit':
            print("Exiting script.")
            break

        dashboard = get_dashboard(uid)
        if dashboard:
            updated_dashboard = update_text_panel(dashboard, user_input)
            push_dashboard(updated_dashboard)
        else:
            print("Could not fetch dashboard for update.")


if __name__ == "__main__":
    dashboard_uid = get_dashboard_uid()
    if dashboard_uid:
        # Start command-line input thread
        input_thread = threading.Thread(target=command_line_input, args=(dashboard_uid,))
        input_thread.start()
    else:
        print("Dashboard UID not found.")

