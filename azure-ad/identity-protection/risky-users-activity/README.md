# Azure AD Risky Users Activity Logger

This Python script uses the Microsoft Graph API to retrieve risky users with a high risk level and their activity logs in the past 14 days. It authenticates with Azure AD using MSAL (Microsoft Authentication Library) and retrieves an access token for making Graph API requests. 

## Prerequisites

- Python 3.x
- `msal` library (can be installed via pip)
- `requests` library (can be installed via pip)
- `tabulate` library (can be installed via pip)

You will also need to create an Azure AD app and set up the necessary credentials. See [Microsoft's documentation](https://docs.microsoft.com/en-us/graph/auth-register-app-v2) for more information.

## Installation

1. Clone the repository or download the script file.
2. Install the necessary dependencies using pip: `pip install -r requirements.txt`
3. Set up your Azure AD app credentials and user settings in the script.

## Usage

1. Run the script: `python main.py`
2. The script will retrieve risky users with a high risk level and their activity logs in the past 14 days using the Microsoft Graph API.
3. The resulting table will be printed to the console and saved as an HTML file.
4. The table will also be copied to your clipboard, so you can easily paste it into another application.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Microsoft Graph API documentation](https://docs.microsoft.com/en-us/graph/)
- [MSAL Python documentation](https://github.com/AzureAD/microsoft-authentication-library-for-python)
- [Requests library documentation](https://requests.readthedocs.io/en/master/)
- [Tabulate library documentation](https://pypi.org/project/tabulate/)

Feel free to customize this README.md file to suit your needs and provide additional information about your project. Good luck with your code!


