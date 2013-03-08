import sys
from xml.etree import ElementTree
from xml.parsers.expat import ExpatError

# from http://code.activestate.com/recipes/410469-xml-as-dictionary/

class XmlListConfig(list):
    def __init__(self, a_list):
        list.__init__(self)
        for element in a_list:
            if element:
                # treat like dict
                if len(element) == 1 or element[0].tag != element[1].tag:
                    self.append(XmlDictConfig(element))
                # treat like list
                else:
                    self.append(XmlListConfig(element))
            elif element.text:
                text = element.text.strip()
                self.append(text)


class XmlDictConfig(dict):
    '''
    Example usage:

    >>> tree = ElementTree.parse('your_file.xml')
    >>> root = tree.getroot()
    >>> xmldict = XmlDictConfig(root)

    Or, if you want to use an XML string:

    >>> root = ElementTree.XML(xml_string)
    >>> xmldict = XmlDictConfig(root)

    And then use xmldict for what it is... a dict.
    '''
    def __init__(self, parent_element, single_item_list=False):
        dict.__init__(self)
        children_names = [child.tag for child in parent_element.getchildren()]
        if parent_element.items():
            self.update(dict(parent_element.items()))
        for element in parent_element:
            if element is not None:
                # treat like dict - we assume that if the first two tags
                # in a series are different, then they are all different.
                if len(element) == 1 or element[0].tag != element[1].tag:
                    a_dict = XmlDictConfig(element)
                # treat like list - we assume that if the first two tags
                # in a series are the same, then the rest are the same.
                else:
                    # here, we put the list in dictionary; the key is the
                    # tag name the list elements all share in common, and
                    # the value is the list itself
                    a_dict = {element[0].tag: XmlListConfig(element)}

                # if the tag has attributes, add those to the dict
                if element.items():
                    a_dict.update(dict(element.items()))
                self._update_or_add_to_tag(element.tag, a_dict, children_names,
                        single_item_list)
            # this assumes that if you've got an attribute in a tag,
            # you won't be having any text. This may or may not be a
            # good idea -- time will tell. It works for the way we are
            # currently doing XML configuration files...
            elif element.items():
                self._update_or_add_to_tag(element.tag, dict(element.items()), children_names,
                        single_item_list)
                #self.update({element.tag: dict(element.items())})
            # finally, if there are no child tags and no attributes, extract
            # the text
            else:
                self._update_or_add_to_tag(element.tag, element.text, children_names,
                        single_item_list)

    def _update_or_add_to_tag(self, tag, item, children_names, single_item_list):
        if children_names.count(tag) > 1:
            try:
                current_value = self[tag]
                current_value.append(item)
                self.update({tag: current_value})
            except: #the first of its kind, an empty list must be created
                #item is written in [], i.e. it will be a list
                self.update({tag: [item]})
        elif single_item_list:
            #item is written in [], i.e. it will be a list
            self.update({tag: [item]})
        else:
            self.update({tag: item})

    @classmethod
    def xml_string_to_dict(cls, xml_string, single_item_list=False,
            set_encoding=None):
        """
            Args:
                xml_string (xml string):
                    The XML fragment to parse, suitably encoded (eg, if setting
                    the 'set_encoding' header to 'utf-8' and the xml_string is
                    unicode, first re-encode xml_string with xml_string.encode('utf-8')).

                single_item_list (boolean flag):
                     Indicates to the parser the XML fragment is a list containg one value.

                set_encoding (string encoding type):
                     If set, add an XML header with the given value for the encoding attr.
        """


        try:
            if set_encoding:
                xml_header = '<?xml version="1.0" encoding="%s" ?>\n' % set_encoding
                xml_string = xml_header + xml_string
                root = ElementTree.fromstring(xml_string)
            else:
                #TODO: Is this a useful feature?
                root = ElementTree.fromstring(xml_string.encode('ascii', 'xmlcharrefreplace'))
        except ExpatError as e:
            print >> sys.stderr, "Failed to parse XML\nXML string was: %s\nError was: %s" % \
                    (xml_string, e)
            return xml_string
        return XmlDictConfig(root, single_item_list)
