============
Introduction
============

The IDS web API provides a way for programmers to use the data and metadata
contained in the datasets that IDS maintains - namely BRIDGE and ELDIS.

The API can be used for search or for retreiving all the metadata about an
asset stored in the IDS datasets.

Root URL
========

The root URL is ``/openapi/``. If you load that URL you will get some example
URLs to load, along with a basic guide to the format, and a link to this
documentation.

Examples
========

To find all documents that mention UNDP you could use:

   ``/openapi/documents/search/short?q=undp``
    
To find all documents that mention UNDP, with an author named "Lopez" you could
use:

   ``/openapi/documents/search/short?q=undp&author=lopez``

To get all the information about asset 1234 you could use:

   ``/openapi/assets/1234/full``

To get all the information about India you could use:

   ``/openapi/countries/1100/full/India``

(Note that you have to know the ID, but the URL will appear this way in search 
results making it easy to read.)

Latest 10 documents on Climate Change

   ``/openapi/documents/search/?q=Climate%20Change&sortDesc=publishDate``

All organisations relating to Peru

   ``/openapi/organisations/search/?q=Peru``

