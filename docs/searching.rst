Searching
=========

URL Format For Searches
-----------------------

.. http:get:: /openapi/(asset_type)/search/(format)?q

   Retrieve list of assets of type `asset_type` matching the search defined by
   `q`. The amount of information returned is controlled by `format` which can
   be one of the following:

   * id - just the id and a URL to get it from
   * short - the id, title and object_type
   * full - all the information available

   If `format` is left blank then the amount returned will be as for "short".
   Extra fields can be requested using the `extra_fields` query parameter - see
   below.

   The `asset_type` can be "assets" to return results across all assets, or one
   of the following to restrict what will be returned:

   * documents
   * organisations
   * themes
   * items
   * subjects
   * sectors
   * countries
   * regions
   * item_types

   :query q: The text to search for
   :query extra_fields: Extra fields to include in the response

   You can request extra fields by using the `extra_fields` query parameter. See
   the `Fields Available`_ section page for details. 

