import json
import requests


def api_method(method):
    def wrapper(self, *args, **kwargs):
        method(self, *args, **kwargs)
        api = self.api
        parameters = self.parameters
        endpoint = '&'.join(['{}={}'.format(key, value) for key, value in parameters.items() if value])
        if not endpoint:
            api_endpoint = api
        else:
            api_endpoint = '{}?{}'.format(api, endpoint)
        response = self.get(api_endpoint)

        return response

    return wrapper


def assert_incident_type(method):
    def wrapper(self, *args, **kwargs):
        incidents = ('', 'crash', 'hazard', 'theft', 'unconfirmed',
                     'infrastructure_issue', 'chop_shop')
        try:
            incident_type = kwargs['incident_type']
        except KeyError:
            method(self, *args, **kwargs)
            return
        if not isinstance(incident_type, str):
            raise TypeError("must pass argument of type str to incident_type")
        if not incident_type.lower() in incidents:
            raise ValueError("allowed arguments for incident_type: {}".format(
                tuple(kwarg for kwarg in incidents)
            ))
        method(self, *args, **kwargs)

    return wrapper


class BaseAPI():
    """Base wraper for individual BikeWise requests."""
    base_url = 'https://bikewise.org:443/api/v2'

    def __init__(self):
        """BikeWise does not require an api key"""
        pass

    def get(self, endpoint):
        """Get request from specified url endpoint."""
        url = '{}/{}'.format(self.base_url, endpoint)
        print(url)
        response = requests.get(url)
        if response.status_code != 200:
            raise ConnectionError("bad request: {}\n"
                                  "requested URL: {}".format(response.status_code, url))
        response_json = json.loads(response.content)

        return response_json


class Incidents(BaseAPI):
    api = 'incidents'

    @api_method
    def __call__(self, page=0, per_page=25):
        self.parameters = {
            'page': page,
            'per_page': per_page
        }

    @api_method
    def id(self, id):
        self.parameters = {
            'id': id}

    @api_method
    @assert_incident_type
    def features(self, page=0, per_page=25, occurred_before=0, occurred_after=0,
                 incident_type="", proximity="", proximity_area=0, query=""):
        self.parameters = {
            'page': page,
            'per_page': per_page,
            'occurred_before': occurred_before,
            'occurred_after': occurred_after,
            'incident_type': incident_type,
            'proximity': proximity,
            'proximity_area': proximity_area,
            'query': query
        }


class Locations(BaseAPI):
    api = 'locations'

    @api_method
    def __call__(self, limit=100, all=False):
        self.parameters = {
            'limit': limit,
            'all': all
        }

    @api_method
    @assert_incident_type
    def features(self, occurred_before=0, occurred_after=0, incident_type="", proximity="",
                 proximity_area=0, query="", limit=100, all=False):
        self.parameters = {
            'occurred_before': occurred_before,
            'occurred_after': occurred_after,
            'incident_type': incident_type,
            'proximity': proximity,
            'proximity_area': proximity_area,
            'query': query,
            'limit': limit,
            'all': all
        }

    @api_method
    @assert_incident_type
    def markers(self, occurred_before=0, occurred_after=0, incident_type="", proximity="",
                proximity_area=0, query="", limit=100, all=False):
        self.api = 'locations/markers'
        self.parameters = {
            'occurred_before': occurred_before,
            'occurred_after': occurred_after,
            'incident_type': incident_type,
            'proximity': proximity,
            'proximity_area': proximity_area,
            'query': query,
            'limit': limit,
            'all': all
        }


class BikeWise():
    incidents = None
    locations = None

    def __init__(self):
        self.incidents = Incidents()
        self.locations = Locations()
