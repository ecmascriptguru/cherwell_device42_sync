import base64
import requests
from .service import Service


class Device42(Service):
    def request(self, path, method, data=(), doql=None):
        headers = {
            'Authorization': 'Basic ' + base64.b64encode((self.user + ':' + self.password).encode()).decode(),
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        result = None

        if method == 'GET':
            response = requests.get(self.url + path, headers=headers, verify=False)
            self.validate_response(response)
            result = self.deserialize_json(response.content.decode())
        if method == 'POST' and doql is not None:
            payload = {
                "query": doql,
                "header": "yes"
            }
            response = requests.post(
                self.url + path,
                headers=headers,
                verify=False,
                data=payload
            )
            validate_response(response)
            result = response.text

        return result
