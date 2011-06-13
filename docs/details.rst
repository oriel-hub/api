Details
=======

URL Formats
-----------

.. http:get:: /a/(asset_type)/search/(format)?q

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

.. http:get:: /a/(asset_type)/(int:asset_id)/(format)

   Retrieve the asset with `asset_id` and return the amount of information as
   indicated by `format`. See above for possible values of `asset_id` and
   `format`.

.. http:get:: /a/(asset_type)/(name)/(format)

   Retrieve the asset with title `name` and return the amount of information as
   indicated by `format`. See above for possible values of `asset_id` and
   `format`.

Fields Available
----------------

You can request extra fields by using the `extra_fields` query parameter. The
available fields vary by asset type. The common fields are:

* title
* more ...

Fields only available to documents are:


Response Format
---------------

The data can be returned as JSON or as XML (or as a nice HTML page which by
default shows formatted JSON - handy for exploring the interface). You specify
which data format you want by using the "Accept" field in the header of
the HTTP GET request. For example, using ``curl`` you would do

    ``curl -X GET -H "Accept: application/json" http://api.ids.ac.uk/a/documents/1234/short``

More about XML formats, Dublin Core etc.
