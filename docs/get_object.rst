=============
Get An Object
=============

URL Formats
===========

Get Single Object
-----------------

.. http:get:: /openapi/(object_type)/(int:object_id)/(format)

.. http:get:: /openapi/(object_type)/(int:object_id)/(format)/(text_name)

   Retrieve the object with **object_id** and return the amount of information as
   indicated by **format** which can be one of the following:

   * id - just the id and a URL to get it from
   * short - the id, title and object_type
   * full - all the information available

   If **format** is left blank then the amount returned will be as for "short".
   Extra fields can be requested using the **extra_fields** query parameter - see
   below.

   The **text_name** field is optional, and is not parsed by the server, but
   can be used to make the URLs more readable.

   The **object_type** can be "objects" to return results across all objects,
   "assets" to return results across all :ref:`assets`, or one of the following
   to restrict what will be returned:

   * documents
   * organisations
   * themes
   * items
   * subjects
   * sectors
   * countries
   * regions
   * itemtypes

   :query extra_fields: Extra fields to include in the response. See below.

   :statuscode 200: Object data returned.
   :statuscode 400: The URL was in an invalid format. There will be a message explaining why.
   :statuscode 404: No object (of type specified) found with that object_id.
   :statuscode 500: There was a server fault. Try again later.

   *Examples:*

   * ``/openapi/objects/C1234/full``
   * ``/openapi/documents/A12345/short``
   * ``/openapi/documents/A12345/``
   * ``/openapi/themes/C1234/id``
   * ``/openapi/countries/A1100/full/India``
   * ``/openapi/documents/A24903/full/undp-human-development-report-1996-highlights``

Get List of Fields
------------------

.. http:get:: /openapi/fieldlist/

   Retrieve the list of fields. The list will name all fields that might appear
   in the entry for an object, though no single object would have all fields -
   some fields will only appear for one type of object. You can use the entries
   from this list to ask for extra fields.

   There are no query parameters for this call, and the status code will be as
   above.

.. _extra-fields:

Extra Fields
============

You can request extra fields by using the **extra_fields** query parameter.
List the fields you want, separating them by commas.

The available fields vary by object type. The complete list of fields can be
seen by using the ``fieldlist`` query - see above. Note that not every object
has every field - in fact no object has every field, as some fields are specific
to one object type or another.

For multiple fields, put a ``+`` in between them. So in order to get the short
format, but add the short and long abstract you would add

  ``extra_fields=short_abstract+long_abstract``

These fields only exist for documents, so we could do:

  ``/openapi/documents/A12345/short?extra_fields=short_abstract+long_abstract``
