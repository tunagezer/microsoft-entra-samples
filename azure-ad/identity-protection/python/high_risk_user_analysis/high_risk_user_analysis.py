import msal
import requests
import datetime
import re
import json
from colorama import init, Fore, Back, Style
import csv
import logging

init(autoreset=True) #automatically reset the color after every print statement

# Optional logging
#logging.basicConfig(level=logging.DEBUG)  # Enable DEBUG log for entire script
#logging.getLogger("msal").setLevel(logging.INFO)  # Optionally disable MSAL DEBUG logs

# Set up the Azure AD app credentials
client_id = 'client_id'
client_secret = 'client_secret'
tenant_id = 'tenant_id'

# MS Graph API settings
api_version = "v1.0"

# MS Graph API settings
api_endpoint = "https://graph.microsoft.com/v1.0/"
api_scope = ["https://graph.microsoft.com/.default"]


# Set the number of days until the user needs to change their password
days_since_last_change = 90
print("Password age:", days_since_last_change)

# Authenticate with Azure AD
app = msal.ConfidentialClientApplication(
    client_id=client_id,
    client_credential=client_secret,
    authority="https://login.microsoftonline.com/" + tenant_id,
    # client_capabilities=["CP1"] # CAE support, just for fun :)
)

# The pattern to acquire a token looks like this.
result = None

# Firstly, looks up a token from cache
#result = app.acquire_token_silent(scopes=api_scope, account=None)

if not result:
#    print("No cached token found, acquiring new token...")
    result = app.acquire_token_for_client(scopes=api_scope)
#else:
#    print("Cached token found, using that.")

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

        # Filter out deleted users
        risky_users = [user for user in risky_users if user["userPrincipalName"] is not None]
        print("Found {} risky users (deleted users filtered out):".format(len(risky_users)))
        print("For the {} users we'll only report those with risky detections involving password spray or leaked credentials.".format(len(risky_users)))

        # Open the CSV files to write the list of users who need to reset their passwords and users who don't need to
        with open('password_reset.csv', mode='w', newline='') as reset_file, open('no_password_reset.csv', mode='w', newline='') as no_reset_file:
            reset_writer = csv.writer(reset_file)
            reset_writer.writerow(['User Principal Name', 'Display Name', 'Risk Last Updated Date'])
            no_reset_writer = csv.writer(no_reset_file)
            no_reset_writer.writerow(['User Principal Name', 'Display Name', 'id', 'Risk Last Updated Date'])
            no_password_reset_user_ids = []

            for user in risky_users:
                # Get risk history for the user
                url = api_endpoint + "identityProtection/riskyUsers/{}/history".format(user["id"])
                response = requests.get(url, headers=headers)

                if response.status_code == 200:
                    result = response.json()
                    if "value" in result:
                        risky_history = result["value"]

                        # Get risky detections with password spray or leaked credentials
                        risky_detections = []
                        for history in risky_history:
                            if "activity" in history and "riskEventTypes" in history["activity"] and ("leakedCredentials" in history["activity"]["riskEventTypes"] or "passwordSpray" in history["activity"]["riskEventTypes"]):
                                risky_detections.append(history)

                        if len(risky_history) > 0:
                            with open('risk_history.json', 'w') as f:
                                json.dump(risky_history, f, indent=4)

                        current_date = datetime.datetime.utcnow()
                        expiration_date = current_date - datetime.timedelta(days=days_since_last_change)
                        expiration_date_str = expiration_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

                        # Get the most recent risky detection for the user
                        most_recent_detection = None
                        for detection in risky_detections:
                            if most_recent_detection is None or detection["riskLastUpdatedDateTime"] > most_recent_detection["riskLastUpdatedDateTime"]:
                                most_recent_detection = detection

                        if most_recent_detection:
                            detection_date_str = re.search(r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})\.\d+Z$', most_recent_detection["riskLastUpdatedDateTime"]).group(1)

                            if detection_date_str > expiration_date_str:
                                print(Fore.RED + "User {} ({}) needs to change password. Risky detection flagged on {} ({} days ago).".format(
                                    most_recent_detection["userDisplayName"], most_recent_detection["userPrincipalName"], detection_date_str, (current_date - datetime.datetime.strptime(detection_date_str, '%Y-%m-%dT%H:%M:%S')).days))

                                # Add the user to the password_reset.csv file
                                reset_writer.writerow([most_recent_detection["userPrincipalName"], most_recent_detection["userDisplayName"], detection_date_str])
                            else:
                                print(Fore.GREEN + "User {} ({}) does not need to change password yet. Risky detection flagged on {} ({} days ago).".format(
                                    most_recent_detection["userDisplayName"], most_recent_detection["userPrincipalName"], detection_date_str, (current_date - datetime.datetime.strptime(detection_date_str, '%Y-%m-%dT%H:%M:%S')).days))

                                # Add the user to the no_password_reset.csv file
                                no_reset_writer.writerow([most_recent_detection["userPrincipalName"], most_recent_detection["userDisplayName"], most_recent_detection["id"],detection_date_str])

                                # Add the user to the dismiss_user.json file
                                no_password_reset_user_ids.append(most_recent_detection["id"])
                                #request_body = json.dumps({"userIds": no_password_reset_user_ids})

                                # Save the JSON request body to a file
                                with open("dismiss_user.json", "w") as outfile:
                                    json.dump({"userIds": no_password_reset_user_ids}, outfile)
else:
    print("No risky users with high risk level found.")