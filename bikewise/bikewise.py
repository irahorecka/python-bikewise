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


class BaseAPI():
  """Base wraper for individual BikeWise requests."""
  base_url = 'https://bikewise.org:443/api/v2'

  def __init__(self):
      """BikeWise does not require an api key"""
      pass

  def get(self, endpoint):
    """Get request from specified url endpoint."""
    url = '{}/{}'.format(self.base_url, endpoint)
    response = requests.get(url)
    if response.status_code != 200:
      raise ConnectionError("Bad request: {}\n"
                            "Requested URL: {}".format(response.status_code, url))
    response_json = json.loads(response.content)

    return response_json


class Incidents(BaseAPI):
    api = 'incidents'

    @api_method
    def __call__(self):
        self.parameters = {}

    @api_method
    def id(self, id):
        self.parameters = {'id': id}

    @api_method
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


class BikeWise():
    incident = None

    def __init__(self):
        self.incidents = Incident()