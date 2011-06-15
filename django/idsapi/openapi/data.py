# class to assemble the data to be returned
import exceptions
import re
from openapi.defines import URL_ROOT, get_hostname, object_name_to_asset_type

class DataMunger():
    def __init__(self, request):
        self.hostname = get_hostname(request)

    def get_required_data(self, result, output_format):
        asset_id = result['asset_id']
        if output_format == 'id':
            return {
                'id': asset_id,
                'url': self._make_url(asset_id, result),
                }
        elif output_format == 'short' or output_format == '':
            return {
                'id': asset_id,
                'url': self._make_url(asset_id, result),
                'object_type': result['object_type'],
                'title': result['title']
                }
        elif output_format == 'full':
            result['url'] = self._make_url(asset_id, result)
            return result
        else:
            raise DataMungerFormatException("the output_format of data returned can be 'id', 'short' or 'full'")

    def _make_url(self, asset_id, result):
        asset_type = object_name_to_asset_type(result['object_type'])
        title = re.sub('\W+', '-', result['title']).lower().strip('-')
        return 'http://' + self.hostname + URL_ROOT + asset_type + '/' + asset_id + '/full/' + title


class DataMungerFormatException(exceptions.Exception):
    def __init__(self, error_text=''):
        Exception.__init__(self)
        self.error_text = 'Data format error: ' + error_text
    def __str__(self):
        return self.error_text
