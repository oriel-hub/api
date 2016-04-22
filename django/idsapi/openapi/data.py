# class to assemble the data to be returned
import sys
import re
import collections

from django.conf import settings
from django.core.urlresolvers import reverse

from openapi import defines
from openapi.xmldict import XmlDictConfig

try:
    from xml.etree.ElementTree import ParseError
except ImportError:
    from xml.parsers.expat import ExpatError as ParseError


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
                object_data = dict((k, v) for k, v in object_data.items() if k not in settings.ADMIN_ONLY_FIELDS)
        else:
            object_data = result

        for xml_field in settings.STRUCTURED_XML_FIELDS:
            if xml_field in object_data:
                try:
                    object_data[xml_field] = self._convert_xml_field(object_data[xml_field])
                except ParseError as e:
                    object_data[xml_field] = "Could not parse XML, issue reported in logs"
                    # and send to logs
                    print >> sys.stderr, \
                        "COULD NOT PARSE XML. object_id: %s, field: %s Error: %s" % \
                        (self.object_id, xml_field, str(e))

        # convert date fields to expected output format
        for date_field in settings.DATE_FIELDS:
            if date_field in object_data:
                object_data[date_field] = object_data[date_field].strftime('%Y-%m-%d %H:%M:%S')

        # add the parent category, if relevant
        if self.object_type in settings.OBJECT_TYPES_WITH_HIERARCHY:
            self._add_child_parent_links(object_data, result)

        if 'description' in object_data:
            object_data['description'] = self._process_description(
                    object_data['description'], user_level_info, beacon_guid)

        object_data['metadata_url'] = self._create_metadata_url(object_name=result['title'])
        return self.fields_sorted(object_data)

    def fields_sorted(self, object_data):
        """Order dicts by keys, returning OrderedDicts"""
        if not isinstance(object_data, dict):
            return object_data

        ordered = collections.OrderedDict()
        for k, v in sorted(object_data.items(), key=lambda (k, v): k):
            # Reorder nested dicts
            if isinstance(v, dict):
                ordered[k] = self.fields_sorted(v)
            # Reorder lists of dicts
            elif isinstance(v, list) or isinstance(v, tuple):
                ordered[k] = [self.fields_sorted(o) for o in v]
            else:
                ordered[k] = v
        return ordered

    def _convert_xml_field(self, xml_field):
        """convert an XML string into a list of dictionaries and add
        metadata URLs"""
        field_dict = XmlDictConfig.xml_string_to_dict(xml_field.encode('utf-8'), True, set_encoding="UTF-8")
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

    def _process_description(self, description, user_level_info, beacon_guid):
        """truncate the description for general level users and
        add an image beacon for most users"""
        # if user_level_info['general_fields_only'] and len(description) > 250:
        #    description = description[:246] + '...'
        # add image beacon
        if user_level_info['image_beacon']:
            description += " <img src='" + settings.IMAGE_BEACON_STUB_URL + \
                '?beacon_guid=' + beacon_guid + "' width='1' height='1'>"
        return description

    def _create_metadata_url(self, object_type=None, object_id=None, object_name=None,
            url_name='object'):
        """create a URL that will give information about the object"""
        if object_type is None:
            object_type = self.object_type
        if object_id is None:
            object_id = self.object_id
        metadata_url = reverse(url_name, kwargs={
            'object_type': object_type,
            'object_id': object_id,
            'output_format': 'full',
            'site': self.site,
        }) + '/'
        if object_name is not None:
            title = re.sub('\W+', '-', object_name).lower().strip('-')
            metadata_url += title + '/'
        return metadata_url

    def _add_child_parent_links(self, object_data, result):
        """Add links to child and parent categories"""
        object_data['children_url'] = self._create_metadata_url(url_name='category_children')

        # TODO: write test for condition when parent links not set
        if not all(field in result for field in ['cat_parent', 'cat_superparent']):
            return

        if result['cat_parent'] != result['cat_superparent']:
            object_data['parent_url'] = self._create_metadata_url(
                    object_id='C' + result['cat_parent'])

        if result['cat_first_parent'] != result['cat_parent'] and \
                result['cat_first_parent'] != result['object_id']:
            object_data['toplevel_parent_url'] = self._create_metadata_url(
                object_id='C' + result['cat_first_parent'])

    def convert_facet_string(self, facet_string, facet_type):
        result = {
            'object_id': '',
            'object_type': '',
            'object_name': '',
            'metadata_url': ''
        }
        if facet_string:
            # is it an XML facet_string
            if settings.FACET_TYPES[facet_type] == "xml_string":
                result = XmlDictConfig.xml_string_to_dict(facet_string.encode('utf-8'), set_encoding="UTF-8")
            elif settings.FACET_TYPES[facet_type] == "id_name_type":
                object_id, object_type, object_name = facet_string.split('|', 2)
                result['object_id'] = object_id
                result['object_name'] = object_name
                result['object_type'] = object_type
            else:
                result['object_name'] = facet_string

            # create metadata url, but only if data exists
            if result['object_id'] and result['object_type'] and result['object_name']:
                result['metadata_url'] = self._create_metadata_url(
                    defines.object_name_to_object_type(result['object_type']),
                    result['object_id'],
                    result['object_name'])

        return result
