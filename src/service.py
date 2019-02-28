import traceback


class Service:
    def __init__(self, settings):
        self.user = settings.attrib["user"]
        self.password = settings.attrib["password"]
        self.url = settings.attrib["url"]
        self.settings = settings
    
    def validate_response(self, response):
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
