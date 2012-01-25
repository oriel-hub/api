# integration tests at the API level
from django.test.testcases import TestCase

from xml.etree import ElementTree

from openapi.xmldict import XmlDictConfig

class XmlDictTestCase(TestCase):

    xml1 = """<OrderNotification>
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

    xml2 = """<Config>
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

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def parse(self, xml):
        root = ElementTree.fromstring(xml)
        return XmlDictConfig(root)

    def test_xml1(self):
        xml1 = self.parse(self.xml1)
        self.assertEqual(xml1['Purchase'][0]['PurchaseId'], 'aaa1')
        self.assertEqual(xml1['Purchase'][1]['PurchaseOrigin'], 'ccc3')

    def test_xml2(self):
        xml2 = self.parse(self.xml2)
        self.assertEqual(xml2['Name'], 'My Config File')
        self.assertEqual(xml2['Items']['Item'][0]['Name'], 'First Item')
        self.assertEqual(xml2['Items']['Item'][1]['Value'], 'Value 2')
