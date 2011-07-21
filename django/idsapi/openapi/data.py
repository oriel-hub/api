# class to assemble the data to be returned
import re
from django.core.urlresolvers import reverse
from openapi import defines

class DataMunger():
    def get_required_data(self, result, output_format):
        object_id = result['object_id']
        if output_format == 'id':
            object_data = {'object_id': object_id}
        elif output_format == 'full':
            object_data = dict((k, v) for k, v in result.items() \
                    if not (k.endswith('_facet') or k in defines.HIDDEN_FIELDS))
            if defines.object_name_to_object_type(result['object_type']) in defines.OBJECT_TYPES_WITH_HIERARCHY:
                self._add_child_parent_links(object_data, object_id, result)
        else:
            object_data = result

        object_data['metadata_url'] = self._make_get_object_url(object_id, result)
        return object_data

    def _make_get_object_url(self, object_id, result):
        object_type = defines.object_name_to_object_type(result['object_type'])
        title = re.sub('\W+', '-', result['title']).lower().strip('-')
        return reverse('object', kwargs = {
            'object_type': object_type,
            'object_id': object_id,
            'output_format': 'full'
            }) + '/' + title + '/'

    def _add_child_parent_links(self, object_data, object_id, result):
        object_type = defines.object_name_to_object_type(result['object_type'])
        object_data['children_url'] = reverse('category_children', kwargs = {
            'object_type': object_type,
            'object_id': object_id,
            'output_format': 'full'
            }) + '/'
        if result['cat_parent'] != result['cat_superparent']:
            object_data['parent_url'] = reverse('object', kwargs = {
                'object_type': object_type,
                'object_id': 'C' + result['cat_parent'],
                'output_format': 'full'
                }) + '/'
        if result['cat_first_parent'] != result['cat_parent'] and \
                result['cat_first_parent'] != result['object_id']:
            object_data['toplevel_parent_url'] = reverse('object', kwargs = {
                'object_type': object_type,
                'object_id': 'C' + result['cat_first_parent'],
                'output_format': 'full'
                }) + '/'
