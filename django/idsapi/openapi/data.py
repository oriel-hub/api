# class to assemble the data to be returned
import re
from django.conf import settings
from django.core.urlresolvers import reverse
from openapi import defines

class DataMunger():
    def get_required_data(self, result, output_format, user_level_info):
        object_id = result['object_id']
        if output_format == 'id':
            object_data = {'object_id': object_id}
        elif output_format == 'full':
            # filter out fields we don't want
            object_data = dict((k, v) for k, v in result.items() if not k.endswith('_facet'))
            if user_level_info['general_fields_only']:
                object_data = dict((k, v) for k, v in object_data.items() if k in settings.GENERAL_FIELDS)
            elif user_level_info['hide_admin_fields']:
                object_data = dict((k, v) for k, v in object_data.items() if not k in settings.ADMIN_ONLY_FIELDS)

            # add the parent category, if relevant
            if defines.object_name_to_object_type(result['object_type']) in defines.OBJECT_TYPES_WITH_HIERARCHY:
                self._add_child_parent_links(object_data, object_id, result)

            # add image beacon to long_abstract
            if object_data.has_key('long_abstract') and user_level_info['image_beacon']:
                object_data['long_abstract'] += '<img src="' + \
                                settings.IMAGE_BEACON_STUB_URL + '" width="1" height="1">'
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
