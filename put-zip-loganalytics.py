import os
import zipfile
import requests
import json
from datetime import datetime
from azure.identity import DefaultAzureCredential
from azure.mgmt.loganalytics import LogAnalyticsDataClient
from azure.mgmt.loganalytics.models import QueryBody

# Define your Azure Data Log Analytics workspace details
workspace_id = "<your_workspace_id>"
workspace_key = "<your_workspace_key>"
log_type = "<your_log_type>"

def unzip_file(zip_file_path, extract_to):
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def send_data_to_log_analytics(workspace_id, workspace_key, log_type, data):
    timestamp = datetime.utcnow().isoformat()
    headers = {
        'Log-Type': log_type,
        'x-ms-date': timestamp,
        'time-generated-field': 'EventTime'
    }
    uri = f"https://{workspace_id}.ods.opinsights.azure.com/api/logs?api-version=2016-04-01"
    body = json.dumps(data)
    response = requests.post(uri, data=body, headers=headers, auth=DefaultAzureCredential())
    response.raise_for_status()

def main():
    try:
        # Unzip the file
        zip_file_path = "<path_to_your_zip_file>"
        extract_to = "<directory_to_extract_to>"
        unzip_file(zip_file_path, extract_to)
        
        # Read the unzipped data and send it to Log Analytics
        log_data = []
        for filename in os.listdir(extract_to):
            with open(os.path.join(extract_to, filename), 'r') as file:
                log_data.extend(file.readlines())
        
        send_data_to_log_analytics(workspace_id, workspace_key, log_type, log_data)
        
        print("Data sent to Azure Data Log Analytics successfully.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
