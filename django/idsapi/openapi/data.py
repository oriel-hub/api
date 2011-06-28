# class to assemble the data to be returned
import re
from openapi.defines import URL_ROOT, object_name_to_asset_type, IdsApiError

class DataMunger():
    def __init__(self, request):
        self.hostname = request.get_host()

    def get_required_data(self, result, output_format):
        asset_id = result['asset_id']
        if output_format == 'id':
            return {
                'id': asset_id,
                'metadata_url': self._make_get_asset_url(asset_id, result),
                }
        elif output_format == 'short' or output_format == '':
            return {
                'id': asset_id,
                'metadata_url': self._make_get_asset_url(asset_id, result),
                'object_type': result['object_type'],
                'title': result['title']
                }
        elif output_format == 'full':
            result = dict((k, v) for k, v in result.items() if not k.endswith('_facet'))
            result['metadata_url'] = self._make_get_asset_url(asset_id, result)
            return result
        else:
            raise DataMungerFormatError("the output_format of data returned can be 'id', 'short' or 'full'")

    def _make_get_asset_url(self, asset_id, result):
        asset_type = object_name_to_asset_type(result['object_type'])
        title = re.sub('\W+', '-', result['title']).lower().strip('-')
        return 'http://' + self.hostname + URL_ROOT + asset_type + '/' + asset_id + '/full/' + title


class DataMungerFormatError(IdsApiError):
    def __init__(self, error_text=''):
        IdsApiError.__init__(self, error_text)
        self.error_text = 'Data format error: ' + error_text
