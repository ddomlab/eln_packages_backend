import elabapi_python
import urllib3

## CONFIGURATION VARIABLES ##
# it is best practice to keep your api keys secret. there is a file, 'api_key',
# in the .gitignore where you should paste your api key as plain text.
# it will not (and should not) be added to any public git repository, and will remain unique for each machine
# new api keys can be generated at https://eln.ddomlab.org/ucp.php?tab=4
API_KEY_PATH = "api_key"
URL = "https://eln.ddomlab.org/api/v2"
PRINTER_PATH = "/home/kyle/Desktop/label.pdf"
##################################################

# allows the connection
urllib3.disable_warnings()

# takes API key from secret file, loads it to elabapi
with open(API_KEY_PATH) as keyfile:
    key = keyfile.read()
configuration = elabapi_python.Configuration()
configuration.api_key["api_key"] = key
configuration.api_key_prefix["api_key"] = "Authorization"
configuration.host = URL
configuration.debug = False
configuration.verify_ssl = False

# create an instance of the API class
api_client = elabapi_python.ApiClient(configuration)

# fix issue with Authorization header not being properly set by the generated lib
api_client.set_default_header(header_name="Authorization", header_value=key)


def load_items_api():
    return elabapi_python.ItemsApi(api_client)


def load_experiments_api():
    return elabapi_python.ExperimentsApi(api_client)


def load_uploads_api():
    return elabapi_python.UploadsApi(api_client)


def load_api():
    return api_client
