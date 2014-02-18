# class to assemble the data to be returned
import sys
import re

from django.conf import settings
from django.core.urlresolvers import reverse

from openapi import defines
from openapi.xmldict import XmlDictConfig

try:
    from xml.etree.ElementTree import ParseError
    assert ParseError  # silence pyflakes error
except ImportError:
    from xml.parsers.expat import ExpatError as ParseError


class DataMunger():

    def __init__(self, site):
        self.site = site
        self.object_id = None
        self.object_type = None

    def get_required_data(self, result, output_format, user_level_info, beacon_guid):
        result = self.create_source_lang_dict(result)
        self.object_id = result[settings.SOLR_UNIQUE_KEY]
        self.object_type = defines.object_name_to_object_type(result['object_type']['eldis'])
        if output_format == 'id':
            object_data = {settings.SOLR_UNIQUE_KEY: self.object_id}
        elif output_format == 'full':
            # filter out fields we don't want
            object_data = dict((k, v) for k, v in result.items() if not k.endswith('_facet'))
            if user_level_info['general_fields_only']:
                object_data = dict((k, v) for k, v in object_data.items() if k in settings.GENERAL_FIELDS)
            elif user_level_info['hide_admin_fields']:
                object_data = dict((k, v) for k, v in object_data.items() if not k in settings.ADMIN_ONLY_FIELDS)
        else:
            object_data = result

        for xml_field in settings.STRUCTURED_XML_FIELDS:
            if xml_field in object_data:
                # assume it is a dictionary of strings - one per source
                # TODO: check this assumption
                for source in object_data[xml_field]:
                    try:
                        object_data[xml_field][source] = \
                            self._convert_xml_field(object_data[xml_field][source])
                    except ParseError as e:
                        object_data[xml_field] = "Could not parse XML, issue reported in logs"
                        # and send to logs
                        print >> sys.stderr, \
                            "COULD NOT PARSE XML. object_id: %s, field: %s Error: %s" % \
                            (self.object_id, xml_field, str(e))

        # convert date fields to expected output format
        #for date_field in settings.DATE_FIELDS:
        #    if date_field in object_data:
        #        for source in object_data[date_field]:
        #            object_data[date_field][source] = \
        #                object_data[date_field][source].strftime('%Y-%m-%d %H:%M:%S')

        # add the parent category, if relevant
        if self.object_type in settings.OBJECT_TYPES_WITH_HIERARCHY:
            self._add_child_parent_links(object_data, result)

        if 'description' in object_data:
            for source in object_data['description']:
                for lang in object_data['description'][source]:
                    object_data['description'][source][lang] = self._process_description(
                        object_data['description'][source][lang], user_level_info, beacon_guid)

        object_data['metadata_url'] = self._create_metadata_url()
        return object_data

    def _convert_xml_field(self, xml_field):
        """convert an XML string into a list of dictionaries and add
        metadata URLs"""
        field_dict = XmlDictConfig.xml_string_to_dict(xml_field.encode('utf-8'), True, set_encoding="UTF-8")
        for _, list_value in field_dict.items():
            for item in list_value:
                if settings.SOLR_UNIQUE_KEY in item and \
                        'object_name' in item and \
                        'object_type' in item:
                    item['metadata_url'] = self._create_metadata_url(
                        defines.object_name_to_object_type(item['object_type']),
                        item[settings.SOLR_UNIQUE_KEY],
                        item['object_name'])
        return field_dict

    def _process_description(self, description, user_level_info, beacon_guid):
        """truncate the description for general level users and
        add an image beacon for most users"""
        #if user_level_info['general_fields_only'] and len(description) > 250:
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
        if object_name:
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
                result['cat_first_parent'] != result[settings.SOLR_UNIQUE_KEY]:
            object_data['toplevel_parent_url'] = self._create_metadata_url(
                object_id='C' + result['cat_first_parent'])

    def field_type_prefix(self, field_name):
        """ take the field name, work out whether it is a generic field,
        has a source, or has both source and language.

        The return is: prefix, source, language
        """
        parts = field_name.split('_')
        if (len(parts) == 1 or parts[-1] == 'id' or
                field_name in settings.GENERIC_FIELD_LIST):
            return field_name, None, None
        # we assume that if the last bit after an underscore is 2 letters
        # then it is a language code, so we have prefix_source_lang
        elif len(parts[-1]) == 2:
            return '_'.join(parts[:-2]), parts[-2], parts[-1]
        else:
            return '_'.join(parts[:-1]), parts[-1], None

    def create_source_lang_dict(self, in_dict):
        out_dict = {}
        for field, value in in_dict.iteritems():
            if field in settings.IGNORE_FIELDS:
                continue
            prefix, source, lang = self.field_type_prefix(field)
            if source is None:
                out_dict[prefix] = value
            else:
                if prefix not in out_dict:
                    out_dict[prefix] = {}
                if lang is None:
                    out_dict[prefix][source] = value
                else:
                    if source not in out_dict[prefix]:
                        out_dict[prefix][source] = {}
                    out_dict[prefix][source][lang] = value
        return out_dict

    def convert_facet_string(self, facet_string):
        result = {
            'object_id': '',
            'object_type': '',
            'object_name': '',
            'metadata_url': ''
        }
        if facet_string:
            # is it an XML facet_string
            if facet_string[0] == '<' and facet_string[-1] == '>':
                result = XmlDictConfig.xml_string_to_dict(facet_string.encode('utf-8'), set_encoding="UTF-8")
            elif facet_string.find('|') > -1:
                object_id, object_type, object_name = facet_string.split('|', 2)
                result[settings.SOLR_UNIQUE_KEY] = object_id
                result['object_name'] = object_name
                result['object_type'] = object_type
            else:
                result['object_name'] = facet_string

            # create metadata url, but only if data exists
            if result[settings.SOLR_UNIQUE_KEY] and result['object_type'] and result['object_name']:
                result['metadata_url'] = self._create_metadata_url(
                    defines.object_name_to_object_type(result['object_type']),
                    result[settings.SOLR_UNIQUE_KEY],
                    result['object_name'])

        return result
