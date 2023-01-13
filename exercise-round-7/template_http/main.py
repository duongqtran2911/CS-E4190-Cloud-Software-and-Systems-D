import os
from google.cloud import storage
import functions_framework
# Add any imports that you may need, but make sure to update requirements.txt

@functions_framework.http
def create_text_file_http(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        Return the fileName in the body of the response.
        Return a HTTP status code of 200.
    Note:
        For more information on how Flask integrates with Cloud
        Functions, see the `Writing HTTP functions` page.
        <https://cloud.google.com/functions/docs/writing/http#http_frameworks>
    """
    
    # TODO: Add logic here

    return