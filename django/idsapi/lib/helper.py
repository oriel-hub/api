from __future__ import unicode_literals, absolute_import


def keep_matching_fields(in_dict, field_list):
    return dict((k, v) for k, v in in_dict.items() if k in field_list)


def keep_not_matching_fields(in_dict, field_list):
    return dict((k, v) for k, v in in_dict.items() if k not in field_list)
