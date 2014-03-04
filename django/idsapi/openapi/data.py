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

    def __init__(self, site, search_params):
        self.site = site
        self.search_params = search_params
        self.item_id = None
        self.item_type = None

    def get_required_data(self, result, output_format, user_level_info, beacon_guid):
        self.item_id = result[settings.SOLR_UNIQUE_KEY]
        self.item_type = defines.item_name_to_item_type(result['item_type'])
        result = self.create_source_lang_dict(result)
        if output_format == 'id':
            object_data = {settings.SOLR_UNIQUE_KEY: self.item_id}
        elif output_format in [None, '', 'short']:
            object_data = {
                settings.SOLR_UNIQUE_KEY: self.item_id,
                'item_type': result['item_type'],
                'title': result['title'],
            }
            if 'extra_fields' in self.search_params:
                fields = self.search_params['extra_fields'].lower().split(' ')
                for field in fields:
                    if field in result:
                        object_data[field] = result[field]
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
                            "COULD NOT PARSE XML. item_id: %s, field: %s Error: %s" % \
                            (self.item_id, xml_field, str(e))

        # convert date fields to expected output format
        #for date_field in settings.DATE_FIELDS:
        #    if date_field in object_data:
        #        for source in object_data[date_field]:
        #            object_data[date_field][source] = \
        #                object_data[date_field][source].strftime('%Y-%m-%d %H:%M:%S')

        # add the parent category, if relevant
        if self.item_type in settings.ITEM_TYPES_WITH_HIERARCHY:
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
                        'item_name' in item and \
                        'item_type' in item:
                    item['metadata_url'] = self._create_metadata_url(
                        defines.item_name_to_item_type(item['item_type']),
                        item[settings.SOLR_UNIQUE_KEY],
                        item['item_name'])
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

    def _create_metadata_url(self, item_type=None, item_id=None, item_name=None,
            url_name='object'):
        """create a URL that will give information about the object"""
        if item_type is None:
            item_type = self.item_type
        if item_id is None:
            item_id = self.item_id
        metadata_url = reverse(url_name, kwargs={
            'item_type': item_type,
            'item_id': item_id,
            'output_format': 'full',
            'site': self.site,
        }) + '/'
        if item_name:
            title = re.sub('\W+', '-', item_name).lower().strip('-')
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
                item_id=result['cat_parent'])

        if result['cat_first_parent'] != result['cat_parent'] and \
                result['cat_first_parent'] != result[settings.SOLR_UNIQUE_KEY]:
            object_data['toplevel_parent_url'] = self._create_metadata_url(
                item_id=result['cat_first_parent'])

    def field_type_prefix(self, field_name):
        """ take the field name, work out whether it is a generic field,
        has a source, or has both source and language.

        The return is: prefix, source, language
        """
        parts = field_name.split('_')
        if (len(parts) == 1 or parts[-1] == 'id' or
                field_name in settings.GENERIC_FIELD_LIST):
            return field_name, None, None
        # we should at this point always have prefix_source_xx
        prefix = '_'.join(parts[:-2])
        source = parts[-2]
        lang = parts[-1]
        return prefix, source, lang

    def create_source_lang_dict(self, in_dict):
        out_dict = {}
        for field_name, value in in_dict.iteritems():
            # we ignore a list of field_names, plus xx_search_api_*
            if (field_name in settings.IGNORE_FIELDS or
                    field_name[2:].startswith('_search_api_') or
                    '_sort_hub_' in field_name or '_search_hub_' in field_name or
                    '_facet_hub_' in field_name):
                continue
            if field_name.startswith('hub_'):
                out_dict[field_name] = value
                continue
            prefix, source, lang = self.field_type_prefix(field_name)
            if source is None:
                out_dict[prefix] = value
            else:
                if prefix not in out_dict:
                    out_dict[prefix] = {}
                # if lang is "zx" then the field is for computers, and may
                # contain multiple languages (eg search, facet fields)
                # if lang is "zz" then language is not relevant (eg date)
                # if lang is "un" then the language is unknown
                if lang == 'zx':
                    continue
                elif lang == 'zz':
                    out_dict[prefix][source] = value
                else:
                    if source not in out_dict[prefix]:
                        out_dict[prefix][source] = {}
                    out_dict[prefix][source][lang] = value
        return out_dict

    def convert_facet_string(self, facet_string):
        result = {
            settings.SOLR_UNIQUE_KEY: '',
            'item_type': '',
            'item_name': '',
            'metadata_url': ''
        }
        if facet_string:
            # is it an XML facet_string
            if facet_string[0] == '<' and facet_string[-1] == '>':
                result = XmlDictConfig.xml_string_to_dict(facet_string.encode('utf-8'), set_encoding="UTF-8")
            elif facet_string.find('|') > -1:
                # TODO: is this an object_id (with prefix char) or actually
                # item_id
                item_id, item_type, item_name = facet_string.split('|', 2)
                result[settings.SOLR_UNIQUE_KEY] = item_id
                result['item_name'] = item_name
                result['item_type'] = item_type
            else:
                result['item_name'] = facet_string

            # create metadata url, but only if data exists
            if result[settings.SOLR_UNIQUE_KEY] and result['item_type'] and result['item_name']:
                result['metadata_url'] = self._create_metadata_url(
                    defines.item_name_to_item_type(result['item_type']),
                    result[settings.SOLR_UNIQUE_KEY],
                    result['item_name'])

        return result
