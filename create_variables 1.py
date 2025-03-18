import os
import grafana_authentication as ga
import requests
from requests.auth import HTTPBasicAuth

class grafana_dashboard:
    def __init__(self, dashboard_title):
        self.dashboard_title = dashboard_title
        self.variables = []
        self.panels = []

    def create_variable(self, variable_name, option_list):
        if option_list:
            options = ','.join(option_list)
            variable = {
                    "name": variable_name,
                    "type": "custom",
                    "label": variable_name,
                    "hide": 0,
                    "query": options,
                    "current": {
                        "text": option_list[0] if option_list else None,
                        "value": option_list[0] if option_list else None
                        },
                    "includeAll": False,
                    "refresh": 1
                    }
            self.variables.append(variable)

    def read_files(self, path):
        file_contents = ""
        try:
            # List all files in the directory
            for filename in os.listdir(path):
                file_path = os.path.join(path, filename)

                # Only read files, ignore directories
                if os.path.isfile(file_path):
                    with open(file_path, 'r') as file:
                        file_contents += file.read() + "\n"  # Add file content to the final string
        except FileNotFoundError:
            return f"Error: The directory {path} was not found."
        except Exception as e:
            return f"An error occurred: {e}"

        return file_contents

    def create_text_panel(self, variable_name, content):
        full_path = f"{dirc}/{variable_name}_logs/${variable_name}"
        file_contents = self.read_files(full_path)
        print(file_contents)
        print(full_path)
        text_panel = {
                "type": "text",
                "title": "Log Summary",
                "gridPos": {
                    "x": 0, 
                    "y": 0,
                    "w": 24,
                    "h": 6
                    },
                
                "options": {
                    "mode": "markdown",
                    "content": f"""
                    ### Summary
                    {content}
                    **selected_path** = {full_path}
                    files = $`{file_contents}`
                    """
                    }
                }
        self.panels.append(text_panel)
    
    def formatted_string(self, string):
        formatted_string = string.replace('_logs', '')
        return formatted_string

    def create_dashboard(self):
        modify_dashboard = {
                "dashboard": {
                    "id": None,
                    "uid": None,
                    "title": self.dashboard_title,
                    "tags": ["Log Viewer"],
                    "timezone": "browser",
                    "schemaVersion": 16,
                    "version": 0,
                    "templating": {
                        "list": self.variables
                        },
                    "panels": self.panels,
                    },
                "overwrite": True
                }
        response = requests.post('http://localhost:3000/api/dashboards/db',
                json = modify_dashboard,
                auth = HTTPBasicAuth(ga.username, ga.password),
                headers = {"Content-Type": "application/json"}
                )
        if response.status_code == 200:
            print("Dashboard created successfully!")
            print("Dashboard URL:", f"http://localhost:3000/d/{response.json()['uid']}")
        else:
            print("Failed to create the dashboard")
            print("Response:", response.text)

def start_dashboard(dashboard, directory):
    for content in os.listdir(directory):
        actual_content = os.path.join(directory, content)
        if os.path.isdir(actual_content):
            options = []
            files = []
            for item in os.listdir(actual_content):
                print(item)
                full_path = os.path.join(actual_content, item)
                print(full_path)
                if os.path.isdir(full_path):
                    formatted_item = dashboard.formatted_string(item)
                    options.append(formatted_item)
                else:
                    files.append(full_path)
            dashboard.create_variable(dashboard.formatted_string(content), options)
            dashboard.create_text_panel(dashboard.formatted_string(content), files)
    dashboard.create_dashboard()

dashboard_handler = grafana_dashboard("Regression Status")
dirc = '/home/yagnald/Desktop/trial_dashboard/logs'
start_dashboard(dashboard_handler, dirc)

