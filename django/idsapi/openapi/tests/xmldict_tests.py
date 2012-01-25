# integration tests at the API level
from django.test.testcases import TestCase

from openapi.xmldict import XmlDictConfig

class XmlDictTestCase(TestCase):

    xml_string1 = """<OrderNotification>
<Purchase>
    <PurchaseId>aaa1</PurchaseId>
    <PurchaseDate>aaa2</PurchaseDate>
    <PurchaseOrigin>aaa3</PurchaseOrigin>
</Purchase>
<Purchase>
    <PurchaseId>ccc1</PurchaseId>
    <PurchaseDate>ccc2</PurchaseDate>
    <PurchaseOrigin>ccc3</PurchaseOrigin>
</Purchase>
</OrderNotification>"""

    xml_string2 = """<Config>
    <Name>My Config File</Name>
    <Items>
    <Item>
        <Name>First Item</Name>
        <Value>Value 1</Value>
    </Item>
    <Item>
        <Name>Second Item</Name>
        <Value>Value 2</Value>
    </Item>
    </Items>
</Config>"""

    xml_mixed_list = """<TopLevel>
    <Item>Some text</Item>
    <Item>Some more text</Item>
    <Item>
        <SubItem>456</SubItem>
        <SubItem>789</SubItem>
    </Item>
</TopLevel>"""

    xml_single_item_list = """<themeList>
<theme>
    <cat_id>153</cat_id>
    <category_name>MDGs health</category_name>
    <deleted>0</deleted>
</theme>
</themeList>"""

    xml_full_list = """<themeList>
<theme>
    <cat_id>153</cat_id>
    <category_name>MDGs health
    </category_name>
    <deleted>0</deleted>
</theme>
<theme>
    <cat_id>179</cat_id>
    <category_name>Children and young people</category_name>
    <deleted>0</deleted>
</theme>
<theme>
    <cat_id>595</cat_id>
    <category_name>Maternal, Newborn and Child Health</category_name>
    <deleted>0</deleted>
</theme>
<theme>
    <cat_id>895</cat_id>
    <category_name>Poverty</category_name>
    <deleted>0</deleted>
</theme>
</themeList>"""

    def test_xml1(self):
        xml_dict = XmlDictConfig.xml_string_to_dict(self.xml_string1)
        self.assertEqual(xml_dict['Purchase'][0]['PurchaseId'], 'aaa1')
        self.assertEqual(xml_dict['Purchase'][1]['PurchaseOrigin'], 'ccc3')

    def test_xml2(self):
        xml_dict = XmlDictConfig.xml_string_to_dict(self.xml_string2)
        self.assertEqual(xml_dict['Name'], 'My Config File')
        self.assertEqual(xml_dict['Items']['Item'][0]['Name'], 'First Item')
        self.assertEqual(xml_dict['Items']['Item'][1]['Value'], 'Value 2')

    def test_mixed_list(self):
        xml_dict = XmlDictConfig.xml_string_to_dict(self.xml_mixed_list)
        self.assertEqual(xml_dict['Item'][0], 'Some text')
        self.assertEqual(xml_dict['Item'][1], 'Some more text')
        self.assertEqual(xml_dict['Item'][2]['SubItem'][0], '456')

    def test_single_item_list(self):
        xml_dict = XmlDictConfig.xml_string_to_dict(self.xml_single_item_list, True)
        self.assertEqual(xml_dict['theme'][0]['category_name'], 'MDGs health')
        xml_dict2 = XmlDictConfig.xml_string_to_dict(self.xml_single_item_list, False)
        self.assertEqual(xml_dict2['theme']['category_name'], 'MDGs health')

    def test_full_list(self):
        xml_dict = XmlDictConfig.xml_string_to_dict(self.xml_full_list, True)
        self.assertEqual(xml_dict['theme'][2]['cat_id'], '595')
        self.assertEqual(xml_dict['theme'][3]['category_name'], 'Poverty')
