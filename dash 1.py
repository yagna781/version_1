import requests
import os

# 🔹 CONFIGURE THESE SETTINGS
GRAFANA_URL = "http://localhost:3000"  # Change if needed
GRAFANA_USERNAME = "admin"  # Your Grafana username
GRAFANA_PASSWORD = "yagna781"  # Your Grafana password
FOLDER_PATH = "/home/nyldivya/Desktop/grafa"  # Change this to your actual directory


class grafanadashboard:
    def __init__(self):
        self.variables = []
        self.panels = []

    def create_dashboard(self,folders,options,files):
        modify_dashboard = {
            "dashboard": {
                "id": None,
                "uid": None,
                "title": "file view",
                "templating": {
                "list": self.variables
                },
                "panels": self.panels,
            },
            "overwrite": True
        }

        response = requests.post(
            'http://localhost:3000/api/dashboards/db',
            json=modify_dashboard,
            auth = (GRAFANA_USERNAME,GRAFANA_PASSWORD),
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            print("Dashboard created successfully")
        else:
            print("failed to create dashboard")


        if options:
            option = ','.join(options)
            variable = {
                    "name": folders,
                    "type": "custom",
                    "label": folders,
                    "hide": 0,
                    "query": option,
                    "current": {
                        "text": options[0] if options else None,
                        "value": options[0] if options else None
                    },
                    "includeAll": False,
                    "refresh": 1
            }
            self.variables.append(variable)

        text_panel = {
                "type": "text",
                "title": f"{folders}",
                "gridPos": {
                    "x": 0, 
                    "y": 0,
                    "w": 24,
                    "h": 7
                },
                "options":{
                    "mode": "markdown",
                    "content": f"""
                        ### {folders}
                        ***files_list***: {files}

                    """
                }
            }
        self.panels.append(text_panel)

def start_dashboard(dashboard,path):
    for folders in os.listdir(path):
        folder_path = os.path.join(path, folders)
        if os.path.isdir(folder_path):
            options = []
            files =[]
            for fol in os.listdir(folder_path):
                hei_1 = os.path.join(folder_path, fol)
                if os.path.isdir(hei_1):
                    options.append(fol)
                else:
                    files.append(hei_1)

            dashboard.create_dashboard(folders,options,files)


dashboard = grafanadashboard()

start_dashboard(dashboard,FOLDER_PATH)






