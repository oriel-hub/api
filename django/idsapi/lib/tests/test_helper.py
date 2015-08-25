from __future__ import unicode_literals, absolute_import

from unittest import TestCase

from ..helper import keep_matching_fields, keep_not_matching_fields


class TestKeepFunctions(TestCase):

    def test_keep_matching_fields(self):
        in_dict = {
            'a': 1,
            'b': 2,
            'c': 3,
            'd': 4,
        }
        field_list = ('a', 'c')
        expected = {
            'a': 1,
            'c': 3,
        }
        self.assertEqual(
            expected,
            keep_matching_fields(in_dict, field_list)
        )

    def test_keep_not_matching_fields(self):
        in_dict = {
            'a': 1,
            'b': 2,
            'c': 3,
            'd': 4,
        }
        field_list = ('a', 'c')
        expected = {
            'b': 2,
            'd': 4,
        }
        self.assertEqual(
            expected,
            keep_not_matching_fields(in_dict, field_list)
        )
