import requests
import urllib.parse as urllib
from src.service import Service

class Cherwell(Service):
    def __init__(self, settings):
        super().__init__(settings)
        headers = {
            'accept': "application/json",
            'content-type': "application/x-www-form-urlencoded",
        }
        data = (
            ('password', bytes(self.password, 'utf-8')),
            ('username', self.user),
            ('client_id', settings.attrib["client_id"]),
            ('grant_type', 'password'),
        )
        payload = urllib.urlencode(data, encoding='latin')
        url = "%s/token" % (self.url,)

        response = requests.request("POST", url, data=payload, headers=headers)
        self.validate_response(response)
        response_data = self.deserialize_json(response.content.decode('utf-8'))
        self.access_token = response_data['access_token']
        self.refresh_token = response_data['refresh_token']

    def refresh_access_token(self):
        headers = {
            'accept': "application/json",
            'content-type': "application/x-www-form-urlencoded",
        }
        data = (
            ('client_id', self.settings.attrib['client_id']),
            ('grant_type', 'refresh_token'),
            ('refresh_token', self.refresh_token),
        )
        payload = urllib.urlencode(data, encoding='latin')
        url = "%s/token" % (self.url,)

        response = requests.request("POST", url, data=payload, headers=headers)
        self.validate_response(response)
        response_data = self.deserialize_json(response.content.decode('utf-8'))
        self.access_token = response_data['access_token']
        self.refresh_token = response_data['refresh_token']

    def request(self, path, method, data=(), silent=False, return_serialized=True):

        def perform_request(path, method, data=()):
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": "Bearer {}".format(self.access_token)
            }

            response = None
            if method == 'GET':
                response = requests.get(self.url + path, headers=headers, verify=False)
            elif method == 'POST':
                response = requests.post(self.url + path, json.dumps(data), headers=headers, verify=False)
            elif method == 'DELETE':
                response = requests.delete(self.url + path, headers=headers, verify=False)

            return response

        result = {}

        if method not in ('GET', 'POST', 'DELETE'):
            return result

        response = perform_request(path, method, data)

        if response.status_code == 401 and self.refresh_token:
            # reauthorize
            self.refresh_access_token()
            # run request again
            response = perform_request(path, method, data)

        if not silent:
            self.validate_response(response)

        if return_serialized:
            if len(response.content):
                result = self.deserialize_json(response.content.decode())
        else:
            result = response

        return result
