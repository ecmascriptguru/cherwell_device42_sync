import json
import base64
import requests
import urllib.parse as urllib
import xml.etree.ElementTree as eTree
import traceback
import lib
from lib import DEBUG
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from sys import exit
from src import Cherwell, Device42, ManageEngine


def deserialize_json(s):
    try:
        return json.loads(s)
    except Exception as err:
        if DEBUG:
            print('Error upon deserialization JSON:', str(err))
            print('Source:', str(s))
            traceback.print_stack()
        else:
            print('Error upon deserialization JSON')
        raise err


def validate_response(response):
    try:
        response.raise_for_status()
    except Exception as err:
        print(err)
        if DEBUG:
            # show states of request and response
            request_state = dict(
                (attr, getattr(response.request, attr, None))
                for attr in ['url', 'method', 'headers', 'body']
            )
            print('Request:', request_state)
            print('Response:', response.__getstate__())
            traceback.print_stack()
        exit(1)


def init_services(settings):
    return {
        'cherwell': Cherwell(settings.find('cherwell')),
        'device42': Device42(settings.find('device42'))
    }


def task_execute(task, services):
    print('Execute task:', task.attrib['description'])

    _resource = task.find('api/resource')
    _target = task.find('api/target')

    if _resource.attrib['target'] == 'cherwell':
        resource_api = services['cherwell']
        target_api = services['device42']
    else:
        resource_api = services['device42']
        target_api = services['cherwell']

    method = _resource.attrib['method']
    doql = _resource.attrib.get('doql')

    source_url = _resource.attrib['path']
    if _resource.attrib.get("extra-filter"):
        source_url += _resource.attrib.get("extra-filter") + "&amp;"
        # source will contain the objects from the _resource endpoint

    if task.attrib.get('type') == 'affinity_group':
        configuration_items = task.findall('configuration-item')

        if doql:
            reset_connections = task.attrib.get('reset-connections') == 'true'
            source = resource_api.request(source_url, method, doql=doql)
            lib.affinity_group_from_d42(
                source,
                _target,
                _resource,
                target_api,
                resource_api,
                configuration_items,
                reset_connections
            )
            return True
        else:
            print("The 'doql' attribute in <resource> is required for this task")
            exit(1)

    mapping = task.find('mapping')
    configuration_item = task.find('configuration-item').attrib['bus-ob-id']

    if _target.attrib.get('delete'):
        lib.delete_objects_from_server(_target, target_api, configuration_item)
        return

    if doql is not None:
        source = resource_api.request(source_url, method, doql=doql)
        lib.from_d42(
            source, mapping,
            _target, _resource,
            target_api, resource_api,
            configuration_item,
            doql=True
        )

    else:
        source = resource_api.request(source_url, method)
        lib.from_d42(
            source, mapping,
            _target, _resource,
            target_api, resource_api,
            configuration_item,
            doql=False
        )

    # source = resource_api.request(source_url, _resource.attrib['method'])
    # lib.from_d42(source, mapping, _target, _resource, target_api, resource_api, configuration_item)

if __name__ == "__main__":
    print('Running...')

    # Load mapping
    config = eTree.parse('mapping.xml')
    meta = config.getroot()

    # Init transports services
    services = init_services(meta.find('settings'))

    # Parse tasks
    tasks = meta.find('tasks')
    for task in tasks:
        if task.attrib['enable'] == 'true':
            task_execute(task, services)
