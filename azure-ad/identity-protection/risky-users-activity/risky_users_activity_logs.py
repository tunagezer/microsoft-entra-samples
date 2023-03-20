import msal
import requests
import datetime
from tabulate import tabulate
import re
import json
import copy
import pyperclip

# Set up the Azure AD app credentials
client_id = 'd1a068c0-aa45-49a1-a3e4-e9b5c5253327'
client_secret = 'U8E8Q~PQKkQOdiNb43hJ87hLJxuMN3IxyDG17cpW'
tenant_id = 'd5499d29-b21e-4166-a994-72e04ca99e79'

# MS Graph API settings
api_endpoint = "https://graph.microsoft.com/beta/"
api_scope = ["https://graph.microsoft.com/.default"]

# User settings
user_principal_name = "user@example.com"

# Authenticate with Azure AD
app = msal.ConfidentialClientApplication(
    client_id=client_id,
    client_credential=client_secret,
    authority="https://login.microsoftonline.com/" + tenant_id
)

result = app.acquire_token_silent(scopes=api_scope, account=None)
if not result:
    result = app.acquire_token_for_client(scopes=api_scope)

if "access_token" in result:
    access_token = result["access_token"]
    print("Acquiring access token... done")

    # Save access token to a file
    with open("access_token.json", "w") as f:
        json.dump(result, f)
        print("Access token saved to file.")
else:
    print(result.get("error"))
    print(result.get("error_description"))
    print(result.get("correlation_id"))
    quit()

# Get risky users with high risk level
url = api_endpoint + "identityProtection/riskyUsers"
params = {
    "$filter": "riskLevel eq 'high'"
}

headers = {
    "Authorization": "Bearer " + access_token,
    "Content-Type": "application/json"
}

print("Getting risky users with high risk level...")
response = requests.get(url, headers=headers, params=params)

if response.status_code == 200:
    result = response.json()
    if "value" in result:
        risky_users = result["value"]
        print("Found {} risky users:".format(len(risky_users)))
        for user in risky_users:
            print("- {} ({}) {}".format(user["userDisplayName"], user["userPrincipalName"], user["riskLastUpdatedDateTime"]))
                        
            # Get activity logs for the user in the past 14 days
            risk_last_updated = user["riskLastUpdatedDateTime"]
            
            # extract date and time from string using regex
            match = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})\.\d+Z', risk_last_updated)
            date_str = match.group(1)

            # convert date string to datetime object
            date = datetime.datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')

            # subtract 14 days from date
            two_weeks_ago = (date - datetime.timedelta(days=14)).date()                 
            
            url = api_endpoint + "auditLogs/signIns"
            params = {
                "$filter": "createdDateTime ge " + two_weeks_ago.isoformat() + " and userPrincipalName eq '" + user["userPrincipalName"] + "'",
                "$orderby": "createdDateTime desc"
            }

            response = requests.get(url, headers=headers, params=params)

            if response.status_code == 200:
                result = response.json()
                if "value" in result:
                    activity_logs = result["value"]
                    print("Found {} activity logs:".format(len(activity_logs)))
                    print(len(activity_logs))
                    with open('activity_logs.json', 'w') as f:
                        f.write(json.dumps(activity_logs, indent=4))

                    # Load data from activity_logs.json file
                    #with open('activity_logs.json', 'r') as f:
                     #   activity_logs = json.load(f)

# Create the table headers
headers = ["Time", "App", "IP Address", "Client App Used", "Resource Display Name", "Location", "Risk Detail", "Risk State", "Device", "Device ID", "Device Display Name", "Operating System", "Browser", "UserAgent", "Compliant?", "Managed?", "Trust Type"]

# Create an empty list to hold the rows
rows = []

# Loop through the activity logs and add each row to the table
for log in activity_logs:
    row = []
    try:
        row.append(log.get("createdDateTime", ""))
        #row.append(log.get("status", ""))
        row.append(log.get("appDisplayName", ""))
        row.append(log.get("ipAddress", ""))
        row.append(log.get("clientAppUsed", ""))
        row.append(log.get("resourceDisplayName", ""))
        location = log.get("location", {})
        geo_coordinates = location.get("geoCoordinates", {})
        geo_coordinates_str = f'{geo_coordinates.get("latitude", "")}, {geo_coordinates.get("longitude", "")}'
        location_str = ", ".join([location.get("city", ""), location.get("state", ""), location.get("countryOrRegion", ""), geo_coordinates_str])
        row.append(location_str)
        row.append(log.get("riskDetail", ""))
        row.append(log.get("riskLevelAggregated", ""))
        row.append(log.get("deviceDisplayName", ""))
        device_detail = log.get("deviceDetail", {})
        row.append(device_detail.get("deviceId", ""))
        row.append(device_detail.get("displayName", ""))
        row.append(device_detail.get("operatingSystem", ""))
        row.append(device_detail.get("browser", ""))
        row.append(log.get("userAgent", ""))
        row.append(device_detail.get("isCompliant", ""))
        row.append(device_detail.get("isManaged", ""))
        row.append(device_detail.get("trustType", ""))
        rows.append(row)
    except Exception as e:
        print(f"Error adding row for log: {log}")
        print(f"Error message: {e}")

# Print the table with adjusted max_width parameter
print(tabulate(rows, headers=headers, tablefmt="grid", numalign="left", disable_numparse=True))
table_html = tabulate(rows, headers=headers, tablefmt="html")

# Save the HTML table to a file
with open("table.html", "w") as f:
    f.write(table_html)
#print(table_html)

# Copy the table string to the clipboard
rows_str = tabulate(rows, headers=headers, tablefmt="grid")
try:
    pyperclip.copy(rows_str)
    print("Table copied to clipboard.")
except Exception as e:
    print(f"Error copying table to clipboard: {e}")