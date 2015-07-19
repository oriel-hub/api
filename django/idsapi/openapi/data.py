# class to assemble the data to be returned
import logging
import re

from django.conf import settings
from django.core.urlresolvers import reverse

from openapi import defines
from openapi.search_builder import InvalidOutputFormat
from openapi.xmldict import XmlDictConfig

try:
    from xml.etree.ElementTree import ParseError
    assert ParseError  # silence pyflakes error
except ImportError:
    from xml.parsers.expat import ExpatError as ParseError

logger = logging.getLogger(__name__)


class DataMunger():

    def __init__(self, site, search_params):
        self.site = site
        self.search_params = search_params
        self.object_id = None
        self.object_type = None

    def _keep_matching_fields(in_dict, field_list):
        return dict((k, v) for k, v in in_dict.items() if k in field_list)

    def _keep_not_matching_fields(in_dict, field_list):
        return dict((k, v) for k, v in in_dict.items() if k not in field_list)

    def _extra_fields(self):
        return self.search_params.get('extra_fields', '').lower().split(' ')

    def _filter_id_fields(self, result):
        return {'object_id': result.get('object_id', result['item_id'])}

    def _filter_short_fields(self, result):
        object_data = {
            'object_id': result.get('object_id', result['item_id']),
            'item_id': result['item_id'],
            'object_type': result.get('object_type', result['item_type']),
            'item_type': result['item_type'],
            'title': result.get('title', result.get('name')),
        }
        for field in self._extra_fields():
            if field in result:
                object_data[field] = result[field]
        return object_data

    def _filter_hub_fields(self, result):
        object_data = self._keep_matching_fields(result, settings.HUB_FIELDS)
        return object_data

    def _filter_full_fields(self, result):
        return result

    def _get_object_data_from_result(self, output_format, result):
        try:
            filter_fn = {
                'id': self._filter_id_fields,
                'short': self._filter_short_fields,
                '': self._filter_short_fields,
                None: self._filter_short_fields,
                'hub': self._filter_hub_fields,
                'full': self._filter_full_fields,
            }[output_format]
        except KeyError:
            raise InvalidOutputFormat(output_format)
        return filter_fn(result)

    def _filter_fields_for_user(self, object_data, user_level_info):
        if user_level_info['general_fields_only']:
            object_data = self._keep_matching_fields(object_data, settings.GENERAL_FIELDS)
        elif user_level_info['hide_admin_fields']:
            object_data = self._keep_not_matching_fields(object_data, settings.ADMIN_ONLY_FIELDS)
        return object_data

    def _convert_date_fields(self, object_data):
        # convert date fields to expected output format
        for date_field in settings.DATE_FIELDS:
            if date_field in object_data:
                for source in object_data[date_field]:
                    object_data[date_field][source] = \
                        object_data[date_field][source].strftime('%Y-%m-%d %H:%M:%S')

    def _convert_descriptions(self, description, user_level_info, beacon_guid):
        for source in description:
            for lang in description[source]:
                if isinstance(description[source][lang], list):
                    description[source][lang][0] = self._process_description(
                        description[source][lang][0], user_level_info, beacon_guid)
                else:
                    description[source][lang] = self._process_description(
                        description[source][lang], user_level_info, beacon_guid)

    def get_required_data(self, result, output_format, user_level_info, beacon_guid):
        self.object_id = result[settings.SOLR_OBJECT_ID]
        self.object_type = defines.object_name_to_object_type(result[settings.SOLR_OBJECT_TYPE])
        result = SourceLangParser(self.search_params).create_source_lang_dict(result)
        object_data = self._get_object_data_from_result(output_format, result)
        object_data = self._filter_fields_for_user(object_data, user_level_info)

        self._convert_xml_field_list(object_data)

        # convert date fields to expected output format
        # self._convert_date_fields(object_data)

        # add the parent category, if relevant
        if self.object_type in settings.OBJECT_TYPES_WITH_HIERARCHY:
            self._add_child_parent_links(object_data, result)

        if 'description' in object_data:
            self._convert_descriptions(
                object_data['description'], user_level_info, beacon_guid)

        object_data['metadata_url'] = self._create_metadata_url()
        return object_data

    def _convert_xml_field_list(self, object_data):
        for xml_field in settings.STRUCTURED_XML_FIELDS:
            if xml_field in object_data:
                # assume it is a dictionary of strings - one per source
                # TODO: check this assumption
                for source in object_data[xml_field]:
                    object_data[xml_field][source] = \
                        self._convert_xml_field(object_data[xml_field][source])

    def _convert_xml_field(self, xml_field):
        """convert an XML string into a list of dictionaries and add
        metadata URLs"""
        if isinstance(xml_field, list):
            newfield = []
            for field in xml_field:
                newfield.append(self._convert_single_xml_field(field, False))
        else:
            newfield = self._convert_single_xml_field(xml_field, True)
        return newfield

    def _convert_single_xml_field(self, xml_field, single_item_list):
        xml_field = xml_field.replace(' & ', '&amp;')
        try:
            field_dict = XmlDictConfig.xml_string_to_dict(
                xml_field.encode('utf-8'), single_item_list, set_encoding="UTF-8")
        except ParseError as e:
            # send to logs
            logger.error(
                "COULD NOT PARSE XML. object_id: %s, field: %s Error: %s" %
                (self.object_id, xml_field, str(e)),
                exc_info=e
            )
            return "Could not parse XML, issue reported in logs"
        self._add_metadata_url_to_xml_fields(field_dict)
        return field_dict

    def _add_metadata_url_to_xml_fields(self, field_dict):
        for list_value in field_dict.values():
            for item in list_value:
                if 'object_id' in item and \
                        'object_name' in item and \
                        'object_type' in item:
                    item['metadata_url'] = self._create_metadata_url(
                        defines.object_name_to_object_type(item['object_type']),
                        item['object_id'],
                        item['object_name'])

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
                object_id=result['cat_parent'].values()[0][0])

        if result['cat_first_parent'] != result['cat_parent'] and \
                result['cat_first_parent'] != result[settings.SOLR_OBJECT_ID]:
            object_data['toplevel_parent_url'] = self._create_metadata_url(
                object_id=result['cat_first_parent'].values()[0][0])

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
                # TODO: is this an object_id (with prefix char) or actually
                # object_id
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


class SourceLangParser(object):

    def __init__(self, search_params):
        self.search_params = search_params

    def create_source_lang_dict(self, in_dict):
        self.out_dict = {}
        self.lang_fields = set()
        self.source_fields = set()
        for field_name, value in in_dict.iteritems():
            self.process_field(field_name, value)
        self.prefer_lang()
        self.prefer_source()
        return self.out_dict

    def process_field(self, field_name, value):
        # we ignore a list of field_names, plus xx_search_api_*
        if self.exclude_field(field_name):
            return
        prefix, source, lang = self.field_type_prefix(field_name)
        if source is None:
            self.out_dict[prefix] = value
        else:
            if prefix not in self.out_dict:
                self.out_dict[prefix] = {}
            # if lang is "zx" then the field is for computers, and may
            # contain multiple languages (eg search, facet fields)
            # if lang is "zz" then language is not relevant (eg date)
            # if lang is "un" then the language is unknown
            if self.exclude_source(source):
                return
            elif self.exclude_lang(lang):
                return
            elif lang == 'zz':
                self.out_dict[prefix][source] = value
                self.source_fields.add(prefix)
            else:
                if source not in self.out_dict[prefix]:
                    self.out_dict[prefix][source] = {}
                self.out_dict[prefix][source][lang] = value
                self.lang_fields.add(prefix)
                self.source_fields.add(prefix)

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

    def exclude_field(self, field_name):
        return (
            field_name in settings.IGNORE_FIELDS or
            field_name[2:].startswith('_search_api_') or
            '_sort_hub_' in field_name or
            '_search_hub_' in field_name or
            '_facet_hub_' in field_name
        )

    def exclude_source(self, source):
        """ check for source_only or source_exclude """
        return (
            (
                'source_only' in self.search_params and
                source != self.search_params['source_only']
            )
            or
            (
                'source_exclude' in self.search_params and
                source == self.search_params['source_exclude']
            )
        )

    def exclude_lang(self, lang):
        """ check for lang_only or lang_exclude """
        if lang == 'zz':
            return False
        # TODO: what about 'un' ??
        return (
            lang == 'zx'
            or
            (
                'lang_only' in self.search_params and
                lang != self.search_params['lang_only']
            )
            or
            (
                'lang_exclude' in self.search_params and
                lang == self.search_params['lang_exclude']
            )
        )

    def prefer_source(self):
        source_pref = self.search_params.get('source_pref', None)
        if source_pref is None:
            return
        for field in self.source_fields:
            # if our preferred source exists, drop all other sources
            if source_pref in self.out_dict[field]:
                self.out_dict[field] = {
                    source_pref: self.out_dict[field][source_pref]
                }

    def prefer_lang(self):
        lang_pref = self.search_params.get('lang_pref', None)
        if lang_pref is None:
            return
        for field in self.lang_fields:
            for source in self.out_dict[field]:
                # if our preferred language exists, drop all other languages
                if lang_pref in self.out_dict[field][source]:
                    self.out_dict[field][source] = {
                        lang_pref: self.out_dict[field][source][lang_pref]
                    }
