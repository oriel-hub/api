# class to assemble the data to be returned
import re
from django.conf import settings
from django.core.urlresolvers import reverse
from openapi import defines
from openapi.xmldict import XmlDictConfig

class DataMunger():
    def __init__(self, site):
        self.site = site
        self.object_id = None
        self.object_type = None

    def get_required_data(self, result, output_format, user_level_info, beacon_guid):
        self.object_id = result['object_id']
        self.object_type = defines.object_name_to_object_type(result['object_type'])
        if output_format == 'id':
            object_data = {'object_id': self.object_id}
        elif output_format == 'full':
            # filter out fields we don't want
            object_data = dict((k, v) for k, v in result.items() if not k.endswith('_facet'))
            if user_level_info['general_fields_only']:
                object_data = dict((k, v) for k, v in object_data.items() if k in settings.GENERAL_FIELDS)
            elif user_level_info['hide_admin_fields']:
                object_data = dict((k, v) for k, v in object_data.items() if not k in settings.ADMIN_ONLY_FIELDS)

            for xml_field in settings.STRUCTURED_XML_FIELDS:
                if xml_field in object_data:
                    object_data[xml_field] = self._convert_xml_field(object_data[xml_field])

            # add the parent category, if relevant
            if self.object_type in settings.OBJECT_TYPES_WITH_HIERARCHY:
                self._add_child_parent_links(object_data, result)

            if 'long_abstract' in object_data:
                object_data['long_abstract'] = self._process_long_abstract(
                        object_data['long_abstract'], user_level_info, beacon_guid)
        else:
            object_data = result

        object_data['metadata_url'] = self._create_metadata_url(object_name=result['title'])
        return object_data

    def _convert_xml_field(self, xml_field):
        """convert an XML string into a list of dictionaries and add
        metadata URLs"""
        field_dict = XmlDictConfig.xml_string_to_dict(xml_field, True)
        for _, list_value in field_dict.items():
            for item in list_value:
                if 'object_id' in item and \
                        'object_name' in item and \
                        'object_type' in item:
                    item['metadata_url'] = self._create_metadata_url(
                            defines.object_name_to_object_type(item['object_type']),
                            item['object_id'],
                            item['object_name'])
        return field_dict

    def _process_long_abstract(self, long_abstract, user_level_info, beacon_guid):
        """truncate the long_abstract for general level users and
        add an image beacon for most users"""
        if user_level_info['general_fields_only'] and len(long_abstract) > 250:
            long_abstract = long_abstract[:246] + '...'
        # add image beacon
        if user_level_info['image_beacon']:
            long_abstract += " <img src='" + settings.IMAGE_BEACON_STUB_URL + \
                    '?beacon_guid=' + beacon_guid + "' width='1' height='1'>"
        return long_abstract

    def _create_metadata_url(self, object_type=None, object_id=None, object_name=None,
            url_name='object'):
        """create a URL that will give information about the object"""
        if object_type == None:
            object_type = self.object_type
        if object_id == None:
            object_id = self.object_id
        metadata_url = reverse(url_name, kwargs = {
            'object_type': object_type,
            'object_id': object_id,
            'output_format': 'full',
            'site': self.site,
            }) + '/'
        if object_name != None:
            title = re.sub('\W+', '-', object_name).lower().strip('-')
            metadata_url += title + '/'
        return metadata_url

    def _add_child_parent_links(self, object_data, result):
        """Add links to child and parent categories"""
        object_data['children_url'] = self._create_metadata_url(url_name='category_children')

        if result['cat_parent'] != result['cat_superparent']:
            object_data['parent_url'] = self._create_metadata_url(
                    object_id='C' + result['cat_parent'])

        if result['cat_first_parent'] != result['cat_parent'] and \
                result['cat_first_parent'] != result['object_id']:
            object_data['toplevel_parent_url'] = self._create_metadata_url(
                    object_id='C' + result['cat_first_parent'])
