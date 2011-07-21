============
Introduction
============

The IDS web API provides a way for programmers to use the data and metadata
contained in the datasets that IDS maintains - namely BRIDGE and ELDIS.

The API can be used for search or for retreiving all the metadata about an
object stored in the IDS datasets.

Root URL
========

The root URL is ``/openapi/``. If you load that URL you will get some example
URLs to load, along with a basic guide to the format, and a link to this
documentation.

Terminology
===========

.. _assets:

Assets
------

The database contains various types of objects, that are either **assets** or
**categories**. **Assets** include documents, organisations, items and
countries, with **categories** include themes, sectors and item types. You can
do a search across all assets, but not across all categories or all objects.
You can search within any type of object though.

Examples
========

To find all documents that mention UNDP you could use:

   ``/openapi/documents/search/short?q=undp``
    
To find all documents that mention UNDP, with an author named "Lopez" you could
use:

   ``/openapi/documents/search/short?q=undp&author=lopez``

To get all the information about object with object ID A1234 you could use:

   ``/openapi/objects/A1234/full``

To get all the information about India you could use:

   ``/openapi/countries/A1100/full/India``

(Note that you only have to know the ID - the name at the end of the URL is
optional, but the URL will appear this way in search results making it easy to
read.)

Latest 10 documents on Climate Change

   ``/openapi/documents/search/?q=Climate%20Change&sortDesc=publishDate``

All organisations relating to Peru

   ``/openapi/organisations/search/?q=Peru``

