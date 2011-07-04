Get An Asset
============

URL Formats
-----------

.. http:get:: /openapi/(asset_type)/(int:asset_id)/(format)

.. http:get:: /openapi/(asset_type)/(int:asset_id)/(format)/(text_name)

   Retrieve the asset with **asset_id** and return the amount of information as
   indicated by **format** which can be one of the following:

   * id - just the id and a URL to get it from
   * short - the id, title and object_type
   * full - all the information available

   If **format** is left blank then the amount returned will be as for "short".
   Extra fields can be requested using the **extra_fields** query parameter - see
   below.

   The **text_name** field is optional, and is not parsed by the server, but
   can be used to make the URLs more readable.

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
   * item_types

   :query extra_fields: Extra fields to include in the response. See below.

   :statuscode 200: Asset data returned.
   :statuscode 400: The URL was in an invalid format. There will be a message explaining why.
   :statuscode 404: No asset (of type specified) found with that asset_id.
   :statuscode 500: There was a server fault. Try again later.

   *Examples:*

   * ``/openapi/assets/1234/full``
   * ``/openapi/documents/12345/short``
   * ``/openapi/documents/12345/``
   * ``/openapi/themes/1234/id``
   * ``/openapi/countries/1100/full/India``
   * ``/openapi/documents/24903/full/undp-human-development-report-1996-highlights``

.. http:get:: /openapi/fieldlist/

   Retrieve the list of fields. The list will name all fields that might appear
   in the entry for an asset, though no single asset would have all fields -
   some fields will only appear for one type of asset. You can use the entries
   from this list to ask for extra fields.

   There are no query parameters for this call, and the status code will be as
   above.

.. _extra-fields:

Extra Fields
------------

You can request extra fields by using the **extra_fields** query parameter.
List the fields you want, separating them by commas.

The available fields vary by asset type. The complete list of fields can be
seen by using the ``fieldlist`` query - see above. Note that not every asset
has every field - in fact no asset has every field, as some fields are specific
to one asset type or another.

For multiple fields, put a ``+`` in between them. So in order to get the short
format, but add the short and long abstract you would add

  ``extra_fields=short_abstract+long_abstract``

These fields only exist for documents, so we could do:

  ``/openapi/documents/12345/short?extra_fields=short_abstract+long_abstract``
