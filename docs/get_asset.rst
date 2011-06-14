Get An Asset
============

URL Formats
-----------

.. http:get:: /openapi/(asset_type)/(int:asset_id)/(format)

   Retrieve the asset with `asset_id` and return the amount of information as
   indicated by `format` which can be one of the following:

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


.. http:get:: /openapi/(asset_type)/(name)/(format)

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
