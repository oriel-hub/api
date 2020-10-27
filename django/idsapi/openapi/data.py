# class to assemble the data to be returned
import logging
import re
import collections

from django.conf import settings
from django.urls import reverse

from lib.helper import keep_matching_fields, keep_not_matching_fields

from openapi import defines
from openapi.search_builder import InvalidOutputFormat, InvalidSolrOutputError
from openapi.xmldict import XmlDictConfig

try:
    from xml.etree.ElementTree import ParseError
    assert ParseError  # silence pyflakes error
except ImportError:
    from xml.parsers.expat import ExpatError as ParseError

logger = logging.getLogger(__name__)
logger.setLevel(getattr(settings, 'LOG_LEVEL', logging.DEBUG))


class DataMunger():
    def __init__(self, site, request=None):
        self.site = site
        self.search_params = search_params
        self.object_id = None
        self.object_type = None
        self.request = request

    def get_required_data(self, result, output_format, user_level_info, beacon_guid):
        self.object_id = result['object_id']
        self.object_type = defines.object_name_to_object_type(result['object_type'])
        if output_format == 'id':
            object_data = {'object_id': self.object_id}
        elif output_format == 'full':
            # filter out fields we don't want
            object_data = dict((k, v) for k, v in list(result.items()) if not k.endswith('_facet'))
            if user_level_info['general_fields_only']:
                object_data = dict((k, v) for k, v in list(object_data.items()) if k in settings.GENERAL_FIELDS)
            elif user_level_info['hide_admin_fields']:
                object_data = dict((k, v) for k, v in list(object_data.items()) if k not in settings.ADMIN_ONLY_FIELDS)
        else:
            object_data = result

        for xml_field in settings.STRUCTURED_XML_FIELDS:
            if xml_field in object_data:
                try:
                    object_data[xml_field] = self._convert_xml_field(object_data[xml_field])
                except ParseError as e:
                    object_data[xml_field] = "Could not parse XML, issue reported in logs"
                    # and send to logs
                    print("COULD NOT PARSE XML. object_id: %s, field: %s Error: %s" % \
                        (self.object_id, xml_field, str(e)), file=sys.stderr)

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
        self.metadata = MetaDataURLCreator(self.object_type, self.object_id, self.site)
        result = SourceLangParser(self.search_params).create_source_lang_dict(result)
        object_data = ObjectDataFilter(self.search_params).filter_results(
            result, output_format, user_level_info)

        self._convert_xml_field_list(object_data)

        # convert date fields to expected output format
        # self._convert_date_fields(object_data)

        if 'description' in object_data:
            self._convert_descriptions(
                object_data['description'], user_level_info, beacon_guid)

        object_data['metadata_url'] = self._create_metadata_url(object_name=result['title'])
        return self.fields_sorted(object_data)

    def fields_sorted(self, object_data):
        """Order dicts by keys, returning OrderedDicts"""
        if not isinstance(object_data, dict):
            return object_data

        ordered = collections.OrderedDict()
        for k, v in sorted(list(object_data.items()), key=lambda k_v: k_v[0]):
            # Reorder nested dicts
            if isinstance(v, dict):
                ordered[k] = self.fields_sorted(v)
            # Reorder lists of dicts
            elif isinstance(v, list) or isinstance(v, tuple):
                ordered[k] = [self.fields_sorted(o) for o in v]
            else:
                ordered[k] = v
        return ordered

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
        field_dict = XmlDictConfig.xml_string_to_dict(xml_field.encode('utf-8'), True, set_encoding="UTF-8")
        for _, list_value in list(field_dict.items()):
            for item in list_value:
                if 'object_id' in item and \
                        'object_name' in item and \
                        'object_type' in item:
                    item['metadata_url'] = self._create_metadata_url(
                            defines.object_name_to_object_type(item['object_type']),
                            item['object_id'],
                            item['object_name'])
        return field_dict

    def _add_metadata_url_to_xml_fields(self, field_dict):
        for value in field_dict.values():
            if isinstance(value, list):
                for item in value:
                    self.metadata.add_url_to_item_if_keys_available(item)
            else:
                self.metadata.add_url_to_item_if_keys_available(value)

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
            title = re.sub(r'\W+', '-', object_name).lower().strip('-')
            metadata_url += title + '/'

        if self.request:
           return self.request.build_absolute_uri(metadata_url)

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
            self.metadata = MetaDataURLCreator(self.object_type, self.object_id, self.site)
            self.metadata.add_url_to_item_if_keys_available(result)
            if result['object_id'] and result['object_type'] and result['object_name']:
                result['metadata_url'] = self.metadata.create_url(
                    defines.object_name_to_object_type(result['object_type']),
                    result['object_id'],
                    result['object_name']
                )

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
                if isinstance(self.out_dict[prefix], basestring):
                    logger.error(
                        "Unexpected source version after non-source version "
                        "already added. field name: %s prefix: %s source: %s "
                        "non-source version: %s source version: %s" %
                        (field_name, prefix, source, self.out_dict[prefix], value)
                    )
                    return
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
        return self.search_params.exclude_source(source)

    def exclude_lang(self, lang):
        if lang == 'zz':
            return False
        if lang == 'zx':
            return True
        return self.search_params.exclude_lang(lang)

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


class ObjectDataFilter(object):
    """ This class filters the field according to the output format and user type
    """
    short_field_list = ('object_id', 'item_id', 'object_type', 'item_type', 'title')

    def __init__(self, search_params):
        self.search_params = search_params

    def _keep_matching_fields_with_defaults(self, in_dict, field_list):
        data = keep_matching_fields(in_dict, field_list)
        for key, backup_key in (
            ('object_id', 'item_id'),
            ('object_type', 'item_type'),
            ('title', 'name')
        ):
            if key in field_list and key not in data:
                data[key] = in_dict[backup_key]
        return data

    def _filter_id_fields(self, result):
        return self._keep_matching_fields_with_defaults(result, ['object_id'])

    def _filter_short_fields(self, result):
        field_list = list(self.short_field_list) + self.search_params.extra_fields()
        return self._keep_matching_fields_with_defaults(result, field_list)

    def _filter_core_fields(self, result):
        field_list = settings.CORE_FIELDS + self.search_params.extra_fields()
        return self._keep_matching_fields_with_defaults(result, field_list)

    def _filter_full_fields(self, result):
        return result

    def _get_object_data_from_result(self, result, output_format):
        try:
            filter_fn = {
                'id': self._filter_id_fields,
                'short': self._filter_short_fields,
                '': self._filter_short_fields,
                None: self._filter_short_fields,
                'core': self._filter_core_fields,
                'full': self._filter_full_fields,
            }[output_format]
        except KeyError:
            raise InvalidOutputFormat(output_format)
        return filter_fn(result)

    def _filter_fields_for_user(self, object_data, user_level_info):
        if user_level_info['general_fields_only']:
            object_data = keep_matching_fields(object_data, settings.GENERAL_FIELDS)
        elif user_level_info['hide_admin_fields']:
            object_data = keep_not_matching_fields(object_data, settings.ADMIN_ONLY_FIELDS)
        return object_data

    def filter_results(self, result, output_format, user_level_info):
        object_data = self._get_object_data_from_result(result, output_format)
        return self._filter_fields_for_user(object_data, user_level_info)


class MetaDataURLCreator(object):

    def __init__(self, object_type, object_id, site):
        self.default_object_type = object_type
        self.default_object_id = object_id
        self.site = site

    def _base_url(self, url_name, object_id, object_type):
        return reverse(
            url_name,
            kwargs={
                'object_type': object_type,
                'object_id': object_id,
                'output_format': 'full',
                'site': self.site,
            }
        ) + '/'

    def _object_name_suffix(self, object_name):
        if object_name:
            return re.sub('\W+', '-', object_name).lower().strip('-') + '/'
        else:
            return ''

    def create_url(
        self, object_type=None, object_id=None, object_name=None, url_name='object'
    ):
        """create a URL that will give information about the object"""
        if object_type is None:
            object_type = self.default_object_type
        if object_id is None:
            object_id = self.default_object_id
        return self._base_url(url_name, object_id, object_type) + \
            self._object_name_suffix(object_name)

    def add_url_to_item_if_keys_available(self, item):
        if (
            isinstance(item, dict) and
            item.get('object_id') and
            item.get('object_name') and
            item.get('object_type')
        ):
            item['metadata_url'] = self.create_url(
                defines.object_name_to_object_type(item['object_type']),
                item['object_id'],
                item['object_name']
            )
