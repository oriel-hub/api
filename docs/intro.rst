Introduction
============

The IDS web API provides a way for programmers to use the data and metadata
contained in the datasets that IDS maintains - namely BRIDGE and ELDIS.

The API can be used for search or for retreiving all the metadata about an
asset stored in the IDS datasets.

Examples
--------

To find all documents that mention UNDP you could use:

   ``/a/documents/search/short?q=undp``
    
To find all documents that mention UNDP, with an author named "Lopez" you could
use:

   ``/a/documents/search/short?q=undp&author=lopez``

To get all the information about asset 1234 you could use:

   ``/a/assets/1234/full``

To get summary information about Angola you could use:

   ``/a/countries/Angola/short``


