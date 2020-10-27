# put start up code here

# Here we work around aparent limitations in sunburnt's escaping. The
# definition of SolrString always escapes whitespace, something that
# doesn't seem needed, nor is correctly handled by the SOLR server
# itself, so we remove whitespace from lucene_special_chars by
# monkeypatching SolrString

from sunburnt.strings import SolrString

SolrString.lucene_special_chars = '+-&|!(){}[]^"~*?:\t\v\\/'
