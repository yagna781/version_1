import requests
from requests.auth import HTTPBasicAuth
import json

class GrafanaDashboardManager:
    def __init__(self, url, username, password, dashboard_title):
        self.url = url
        self.auth = HTTPBasicAuth(username, password)
        self.dashboard_title = dashboard_title
        self.headers = {"Content-Type": "application/json"}

    def get_dashboard_uid(self):
        """Fetch the UID of the dashboard based on its title."""
        response = requests.get(f"{self.url}/api/search?query={self.dashboard_title}", auth=self.auth)
        if response.status_code == 200:
            dashboards = response.json()
            if dashboards:
                return dashboards[0]['uid']
        return None  # Dashboard not found

    def create_dashboard(self):
        """Create a new dashboard with a text panel."""
        dashboard_payload = {
            "dashboard": {
                "id": None,
                "uid": None,
                "title": self.dashboard_title,
                "panels": [
                    {
                        "type": "text",
                        "title": "Text Panel",
                        "gridPos": {"x": 0, "y": 0, "w": 24, "h": 5},
                        "options": {
                            "content": "Initial Text",
                            "mode": "html"  # Mode can be 'markdown' or 'html'
                        }
                    }
                ],
                "schemaVersion": 30,
                "version": 1
            },
            "overwrite": False
        }

        response = requests.post(f"{self.url}/api/dashboards/db", headers=self.headers, auth=self.auth, data=json.dumps(dashboard_payload))

        if response.status_code == 200:
            print("Dashboard created successfully!")
            return response.json()['uid']
        else:
            print(f"Failed to create dashboard: {response.status_code} - {response.text}")
            return None

    def get_dashboard(self, uid):
        """Fetch the existing dashboard configuration using UID."""
        response = requests.get(f"{self.url}/api/dashboards/uid/{uid}", auth=self.auth)
        if response.status_code == 200:
            print("dashboard is ok")
            return response.json()
        else:
            print(f"Failed to fetch dashboard: {response.status_code} - {response.text}")
            return None

    def append_text_to_panel(self, dashboard, new_text):
        """Append new text to the existing text panel."""
        panels = dashboard['dashboard']['panels']
        text_panel_found = False

        for panel in panels:
            if panel['type'] == 'text':
                text_panel_found = True
                existing_content = panel['options'].get('content', '')
                panel['options']['content'] = existing_content + "<br>" + new_text
                print("text appended")
                break  # Assuming there's only one text panel

        if not text_panel_found:
            print("No text panel found in the dashboard.")
        return dashboard

    def push_dashboard(self, updated_dashboard):
        """Push the updated dashboard back to Grafana."""
        payload = {
            "dashboard": updated_dashboard['dashboard'],
            "overwrite": True
        }

        response = requests.post(f"{self.url}/api/dashboards/db", headers=self.headers, auth=self.auth, data=json.dumps(payload))

        if response.status_code == 200:
            print("Dashboard updated successfully!")
        else:
            print(f"Failed to update dashboard: {response.status_code} - {response.text}")

    def run(self):
        dashboard_uid = self.get_dashboard_uid()

        # If dashboard does not exist, create one
        if not dashboard_uid:
            print("Dashboard not found. Creating a new dashboard...")
            dashboard_uid = self.create_dashboard()
            if not dashboard_uid:
                print("Failed to create the dashboard. Exiting...")
                return

        while True:
            new_text = input("Enter the text to add to the Grafana panel (type 'exit' to quit): ")

            if new_text.lower() == 'exit':
                print("Exiting...")
                break

            dashboard = self.get_dashboard(dashboard_uid)
                 if dashboard:
                updated_dashboard = self.append_text_to_panel(dashboard, new_text)
                self.push_dashboard(updated_dashboard)
            else:
                print("Could not fetch dashboard for update.")


if __name__ == "__main__":
    grafana_manager = GrafanaDashboardManager(
        url="http://localhost:3000",
        username="admin",
        password="yagna781",
        dashboard_title="text Panel"
    )
    grafana_manager.run()


