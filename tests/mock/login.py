"""Mock Skybell Login Response."""

from tests.mock import ACCESS_TOKEN
from tests.mock import USERID


def post_response_ok(access_token=ACCESS_TOKEN, user_id=USERID):
    """Return the successful login response json."""
    return '''
    {
        "firstName": "John",
        "lastName": "Doe",
        "resourceId": "resourceid123",
        "createdAt": "2016-11-26T22:30:45.254Z",
        "updatedAt": "2016-11-26T22:30:45.254Z",
        "id": "'''+user_id+'''",
        "userLinks": [],
        "access_token": "'''+access_token+'''"
    }'''