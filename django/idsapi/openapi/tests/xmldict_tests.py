# -*- coding: utf-8 -*-
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

    def test_xml1(self):
        xml_dict = XmlDictConfig.xml_string_to_dict(self.xml_string1)
        self.assertEqual(xml_dict['Purchase'][0]['PurchaseId'], 'aaa1')
        self.assertEqual(xml_dict['Purchase'][1]['PurchaseOrigin'], 'ccc3')

    xml_string2 = """<Config>
    <Name>My Config File</Name>
    <AltName use="short">myconf</AltName>
    <Config x="y" />
    <Items>
    <Item p="q">
        <Name>First Item</Name>
        <Value>Value 1</Value>
    </Item>
    <Item>
        <Name>Second Item</Name>
        <Value>Value 2</Value>
    </Item>
    </Items>
</Config>"""

    def test_xml2(self):
        xml_dict = XmlDictConfig.xml_string_to_dict(self.xml_string2)
        self.assertEqual(xml_dict['Name'], 'My Config File')
        self.assertEqual(xml_dict['AltName']['use'], 'short')
        self.assertEqual(xml_dict['Config']['x'], 'y')
        self.assertEqual(xml_dict['Items']['Item'][0]['p'], 'q')
        self.assertEqual(xml_dict['Items']['Item'][0]['Name'], 'First Item')
        self.assertEqual(xml_dict['Items']['Item'][1]['Value'], 'Value 2')

    xml_mixed_list = """<TopLevel>
    <Item>Some text</Item>
    <Item>Some more text</Item>
    <Item>
        <SubItem>456</SubItem>
        <SubItem>789</SubItem>
        <SubItem></SubItem>
        <SubItem>
            <SubSubItem>654</SubSubItem>
            <SubSubItem>987</SubSubItem>
        </SubItem>
    </Item>
</TopLevel>"""

    def test_mixed_list(self):
        xml_dict = XmlDictConfig.xml_string_to_dict(self.xml_mixed_list)
        self.assertEqual(xml_dict['Item'][0], 'Some text')
        self.assertEqual(xml_dict['Item'][1], 'Some more text')
        self.assertEqual(xml_dict['Item'][2]['SubItem'][0], '456')
        self.assertEqual(xml_dict['Item'][2]['SubItem'][2][1], '987')

    xml_single_item_list = """<themeList>
<theme>
    <cat_id>153</cat_id>
    <category_name>MDGs health</category_name>
    <deleted>0</deleted>
</theme>
</themeList>"""

    def test_single_item_list(self):
        xml_dict = XmlDictConfig.xml_string_to_dict(self.xml_single_item_list,
                single_item_list=True)
        self.assertEqual(xml_dict['theme'][0]['category_name'], 'MDGs health')
        xml_dict2 = XmlDictConfig.xml_string_to_dict(self.xml_single_item_list,
                single_item_list=False)
        self.assertEqual(xml_dict2['theme']['category_name'], 'MDGs health')

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

    def test_full_list(self):
        xml_dict = XmlDictConfig.xml_string_to_dict(self.xml_full_list,
                single_item_list=True)
        self.assertEqual(xml_dict['theme'][2]['cat_id'], '595')
        self.assertEqual(xml_dict['theme'][3]['category_name'], 'Poverty')

    xml_non_ascii_text = u"""<themeList>
<theme>
    <cat_id>153</cat_id>
    <category_name>Stäckövérfløw</category_name>
    <deleted>0</deleted>
</theme>
</themeList>"""

    def test_utf8_encoded_string_input(self):
        xml_dict = XmlDictConfig.xml_string_to_dict(self.xml_non_ascii_text.encode('utf-8'),
                single_item_list=True, set_encoding="UTF-8")
        self.assertEqual(xml_dict['theme'][0]['category_name'], u'Stäckövérfløw')

    def test_utf8_unicode_string_input(self):
        #TODO: This is testing the conversion of unicode to ascii.
        xml_dict = XmlDictConfig.xml_string_to_dict(self.xml_non_ascii_text,
                single_item_list=True)
        self.assertEqual(xml_dict['theme'][0]['category_name'], u'Stäckövérfløw')

    trouble_text = """
<languageList><language><isocode>en</isocode><title>Workshop on women and disability</title><description>The Secretary General of Argentina's National Commission Advisor on the Integration of Disabled People, Comisión Nacional Asesora para la Integración de Personas Discapacitadas (CONADIS), Prof. Silvia Bersanelli wrote on International Women's Day 2010 that disabled women are among the most marginalised groups in the world. Over half of disabled people in Argentina are women, more than one million inhabitants. These women typically suffer from double, triple or multi-dimensional discrimination. To address this situation, the national government of Argentina established the Gender and Disability Group in 2004, which coordinates CONADIS and convened this workshop. The papers submitted for this workshop encompass a variety of topics and strategies to develop more inclusive, just and equitable social relations in Argentina. For example, Dr. Norma Picaso submitted a paper on disabled women and access to health. Other papers address issues of violence, work, sexual and reproductive rights, the inclusion of disabled women in the feminist movement, etcetera.&#x0D;
&#x0D;
This web page - http://www.conadis.gov.ar/boletines.html - contains links to the following workshop papers: &#x0D;
&#x0D;
#7; Presentación. Silvia Bersanelli. Secretaria General. CONADIS. (PDF) - (DOC) / (PDF) - (DOC)&#x0D;
#7; Acceso a la Salud. Mujeres con Discapacidad. Norma Picaso. (PDF) - (DOC)&#x0D;
#7; Violencia y Mujeres con Discapacidad. Carlos Borro. (PDF) - (DOC)&#x0D;
#7; Moda-Diseño -Discapacidad: el derecho a vestirse. Silvia Valori. (PDF)-(DOC)&#x0D;
#7; Discriminación y Mujeres con Discapacidad. Mercedes Monjaime. (PDF)-(DOC)</description><language_id>1</language_id></language><language><isocode>es</isocode><title>Jornada mujer y discapacidad</title><description>The Secretary General of Argentina's National Commission Advisor on the Integration of Disabled People, Comisión Nacional Asesora para la Integración de Personas Discapacitadas (CONADIS), Prof. Silvia Bersanelli wrote on International Women's Day 2010 that disabled women are among the most marginalised groups in the world. Over half of disabled people in Argentina are women, more than one million inhabitants. These women typically suffer from double, triple or multi-dimensional discrimination. To address this situation, the national government of Argentina established the Gender and Disability Group in 2004, which coordinates CONADIS and convened this workshop. The papers submitted for this workshop encompass a variety of topics and strategies to develop more inclusive, just and equitable social relations in Argentina. For example, Dr. Norma Picaso submitted a paper on disabled women and access to health. Other papers address issues of violence, work, sexual and reproductive rights, the inclusion of disabled women in the feminist movement, etcetera.&#x0D;
&#x0D;
This webpage - http://www.conadis.gov.ar/boletines.html - contains links to workshop papers: &#x0D;
#7; Presentación. Silvia Bersanelli. Secretaria General. CONADIS. (PDF) - (DOC) / (PDF) - (DOC)&#x0D;
#7; Acceso a la Salud. Mujeres con Discapacidad. Norma Picaso. (PDF) - (DOC)&#x0D;
#7; Violencia y Mujeres con Discapacidad. Carlos Borro. (PDF) - (DOC)&#x0D;
#7; Moda-Diseño -Discapacidad: el derecho a vestirse. Silvia Valori. (PDF)-(DOC)&#x0D;
#7; Discriminación y Mujeres con Discapacidad. Mercedes Monjaime. (PDF)-(DOC)</description><language_id>429</language_id></language></languageList>
"""

    def test_trouble_text(self):
        try:
            XmlDictConfig.xml_string_to_dict(self.trouble_text,
                single_item_list=False)
        except Exception as e:
            self.fail('Failed to convert trouble_text to dictionary.  '
                      'Exception was: %s' % e)
