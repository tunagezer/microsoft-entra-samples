# Azure AD Risky Users Activity Logger

This Python script is a sample that demonstrates how to use the Microsoft Graph API to retrieve risky users with a high risk level and their activity logs in the past 14 days. It authenticates with Azure AD using MSAL (Microsoft Authentication Library) and retrieves an access token for making Graph API requests. 

This sample code can be used as a starting point to investigate risky users in Azure AD Identity Protection, as documented in [Microsoft's Azure AD Identity Protection documentation](https://docs.microsoft.com/en-us/azure/active-directory/identity-protection/howto-identity-protection-investigate-risk).

## Prerequisites

- Python 3.x
- `msal` library (can be installed via pip)
- `requests` library (can be installed via pip)
- `tabulate` library (can be installed via pip)

You will also need to create an Azure AD app and set up the necessary credentials. See [Microsoft's documentation](https://docs.microsoft.com/en-us/graph/auth-register-app-v2) for more information.

## Installation

1. Clone the repository or download the script file.
2. Install the necessary dependencies using pip: `pip install -r requirements.txt`
3. Set up your Azure AD app credentials in the script.
4. Replace the following variables in the script with your own values:
    - `client_id`: Your Azure AD app client ID.
    - `client_secret`: Your Azure AD app client secret.
    - `tenant_id`: Your Azure AD tenant ID.

## Usage

1. Run the script: `python risky_users_activity_logs.py`
2. The script will retrieve risky users with a high risk level and their activity logs in the past 14 days using the Microsoft Graph API.
3. The resulting table will be printed to the console and saved as an HTML file.
4. The table will also be copied to your clipboard, so you can easily paste it into another application.
5. The access token used to make the Graph API requests will be saved to a file named `access_token.json` in the execution folder.
6. The user activity logs will be saved to a file named `activity_logs.json` in the execution folder.

## Disclaimer

This script is provided as a sample for educational purposes only. It is your responsibility to ensure that your use of this script complies with all applicable laws, regulations, and policies. The script author and Microsoft make no representation or warranty as to the completeness, accuracy, or suitability of this script. The script author and Microsoft disclaim any liability arising out of your use of this script.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Microsoft Graph API documentation](https://docs.microsoft.com/en-us/graph/)
- [MSAL Python documentation](https://github.com/AzureAD/microsoft-authentication-library-for-python)
- [Requests library documentation](https://requests.readthedocs.io/en/master/)
- [Tabulate library documentation](https://pypi.org/project/tabulate/)
- [Azure AD Identity Protection documentation](https://docs.microsoft.com/en-us/azure/active-directory/identity-protection/howto-identity-protection-investigate-risk)

Good luck with your Investigation!



