Searching
=========

URL Format For Searches
-----------------------

.. http:get:: /openapi/(asset_type)/search/(format)?q

   Retrieve list of assets of type **asset_type** matching the search defined by
   **q**. The amount of information returned is controlled by **format** which can
   be one of the following:

   * id - just the id and a URL to get it from
   * short - the id, title and object_type
   * full - all the information available

   If **format** is left blank then the amount returned will be as for "short".
   Extra fields can be requested using the **extra_fields** query parameter - see
   the :ref:`extra-fields` section for details. 

   The **asset_type** can be "assets" to return results across all assets, or one
   of the following to restrict what will be returned:

   * documents
   * organisations
   * themes
   * items
   * subjects
   * sectors
   * countries
   * regions
   * itemtypes

   Query fields that take text as the argument to search for. 

   :query q: The text to search for. Note the search is not case-sensitive.
   :query country: The name of a country to search for.
   :query keyword: The name of a keyword to search for.
   :query region: The name of a region to search for.
   :query sector: The name of a sector to search for.
   :query subject: The name of a subject to search for.
   :query source: The name of a source to search for - currently 'eldis' or 'bridge'
   :query theme: The name of a theme to search for.

   Note that you can use ``*`` in your query, but not as the first character.
   So you can use:

   ``/openapi/documents/search/full?keyword=af*``
   ``/openapi/documents/search/full?keyword=af*ca``

   but not:

   ``/openapi/documents/search/full?keyword=*ca``

   Date based query fields:

   :query metadata_published_after: Date after which the metadata was published.
   :query metadata_published_before: Date before which the metadata was published.
   :query metadata_published_year: The metadata was published during the specified year.

   For the first two, the date should be specified as YYYY-MM-DD (year, month,
   day). For the last option, the value is just the 4 digit year.

   Special query fields:

   :query all: Used by itself to just return all items.
   :query extra_fields: Extra fields to include in the response (*not implemeted yet*)

   Note that each query parameter can only be included once in the query. If
   you do so the API will return with a status of 400 and a message telling you
   which parameter was repeated.

   :statuscode 200: Asset data returned.
   :statuscode 400: The URL was in an invalid format. There will be a message explaining why.
   :statuscode 500: There was a server fault. Try again later.


Combining Search Terms
----------------------

If you have multiple search terms in the query parameters, then the items
returned will be those that match *all* of the search terms. To put it another
way, they will be combined with an **AND** in boolean terms.

Within a query parameter you can combine terms using either **AND** or **OR** using
the ``&`` and ``|`` characters respectively - though these characters must be *URL
encoded*. ``&`` becomes ``%26`` and ``|`` becomes ``%7C``. Note that you can only use
one of these within a single query parameter. 

If you include a space (URL encoded as ``%20``) the terms will be considered a
single string. So ``q=climate%20change`` will search for anything containing
*"climate change"*.

To give some examples:

* To search for assets that are concerned with Climate Change:
   * ``theme=climate change`` (before being URL encoded)
   * ``theme=climate%20change`` (after being URL encoded)

* To search for assets that are concerned with either Angola or Lesotho:
   * ``country=angola|lesotho`` (before being URL encoded)
   * ``country=angola%7Clesotho`` (after being URL encoded)

* To search for assets that are concerned with any of Angola, Lesotho or Namibia:
   * ``country=angola|lesotho|namibia`` (before being URL encoded)
   * ``country=angola%7Clesotho%7Cnamibia`` (after being URL encoded)

* To search for assets that are concerned with both Angola and Lesotho:
   * ``country=angola&lesotho`` (before being URL encoded)
   * ``country=angola%26lesotho`` (after being URL encoded)

* The following would be an illegal query - you cannot use both the AND and OR terms in a single query parameter.
   * ``country=angola|lesotho&namibia`` (before being URL encoded)
   * ``country=angola%7Clesotho%26namibia`` (after being URL encoded)

* The following is entirely legal. It will search for items that are concerned both with Angola and South Africa, *and* have a theme of either gender or climate change.    
   * ``country=angola&south africa & theme=gender|climate change`` (before being URL encoded)
   * ``country=angola%26south%20africa&theme=gender%7Cclimate%20change`` (after being URL encoded)

Note that in the last example, in the pre-encoded version the middle ``&`` is
separated by a space - this is because it is the character to combine query
parameters.  Make sure you encode each query parameter value separately and then
combine them, rather than combining them and then encoding the whole query
string. Also don't encode the ``=`` characters. For the above example you could
encode the URL with (in pseudo-code)::

   url = url_root + 'assets/search/?' 
   url += 'country=' + url.encode('angola&lesotho')
   url += 'theme=' + url.encode('gender|climate change')

Example Searches
----------------

To find all entries that mention UNDP you would use:

   ``/openapi/assets/search/short?q=undp``
    
To find all entries that mention UNDP, with a keyword of gender you would use:

   ``/openapi/assets/search/short?q=undp&keyword=gender``

To find all documents that refer to both Angola *and* South Africa, and that
have a theme or either gender or climate change, you would use:
    
   ``/openapi/documents/search/full?country=angola%26South%20Africa&theme=gender|climate%20change``

To find all documents that mention UNDP, with an author named "Lopez" you could
use:

   ``/openapi/documents/search/short?q=undp&author=lopez``

*Note:* the author field is not implemented yet.

Latest 10 documents on Climate Change

   ``/openapi/documents/search/?q=Climate%20Change&sortDesc=publishDate``

*Note:* the sortDesc (and sortAsc) fields have not been implemented yet.

All organisations relating to Peru

   ``/openapi/organisations/search/?q=Peru``

