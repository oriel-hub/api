# class to assemble the data to be returned
import re
from django.core.urlresolvers import reverse
from openapi import defines

class DataMunger():
    def get_required_data(self, result, output_format):
        asset_id = result['asset_id']
        if output_format == 'id':
            asset_data = {'asset_id': asset_id}
        elif output_format == 'full':
            asset_data = dict((k, v) for k, v in result.items() \
                    if not (k.endswith('_facet') or k in defines.HIDDEN_FIELDS))
            if defines.object_name_to_asset_type(result['object_type']) in defines.ASSET_TYPES_WITH_HIERARCHY:
                self._add_child_parent_links(asset_data, asset_id, result)
        else:
            asset_data = result

        asset_data['metadata_url'] = self._make_get_asset_url(asset_id, result)
        return asset_data

    def _make_get_asset_url(self, asset_id, result):
        asset_type = defines.object_name_to_asset_type(result['object_type'])
        title = re.sub('\W+', '-', result['title']).lower().strip('-')
        return reverse('asset', kwargs = {
            'asset_type': asset_type,
            'asset_id': asset_id,
            'output_format': 'full'
            }) + '/' + title + '/'

    def _add_child_parent_links(self, asset_data, asset_id, result):
        asset_type = defines.object_name_to_asset_type(result['object_type'])
        asset_data['children_url'] = reverse('category_children', kwargs = {
            'asset_type': asset_type,
            'asset_id': asset_id,
            'output_format': 'full'
            }) + '/'
        if result['cat_parent'] != result['cat_superparent']:
            asset_data['parent_url'] = reverse('asset', kwargs = {
                'asset_type': asset_type,
                'asset_id': result['cat_parent'],
                'output_format': 'full'
                }) + '/'
        if result['cat_first_parent'] != result['cat_parent'] and \
                result['cat_first_parent'] != result['asset_id']:
            asset_data['toplevel_parent_url'] = reverse('asset', kwargs = {
                'asset_type': asset_type,
                'asset_id': result['cat_first_parent'],
                'output_format': 'full'
                }) + '/'
