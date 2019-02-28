import json, base64, requests
import xml.etree.ElementTree as eTree
import urllib.parse as urllib
from .service import Service

class ManageEngine(object):
    class OPERATION_NAME:
        read = 'read'
        add = 'add'
        update = 'update'
        delete = 'delete'

    OPERATION_NAMES = [
        OPERATION_NAME.read,
        OPERATION_NAME.update,
        OPERATION_NAME.add,
        OPERATION_NAME.delete
    ]

    def __init__(self, settings):
        if not settings.attrib.get('url') or not settings.attrib.get('technician_key'):
            raise ImportError('url and technician_key option is required in ManageEngine')

        self.url = settings.attrib.get('url')
        self.technician_key = settings.attrib.get('technician_key')

    def request(self, path, method='POST', data=(), silent=False, return_serialized=True):
        def perform_request(path, method, data=()):
            headers = {
                "Content-Type": "application/xml",
                "Accept": "application/json",
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
            raise Exception('Your key is invalid or expired.')

        if not silent:
            self.validate_response(response)

        if return_serialized:
            if len(response.content):
                result = self.deserialize_json(response.content.decode())
        else:
            result = response

        return result


if __name__ == "__main__":
    config = eTree.parse('mapping.xml')
    meta = config.getroot()

    # Init transports services
    settings = meta.find('settings')
    item = ManageEngin(settings.find('manage_engine'))