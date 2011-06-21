Response Details
================

Response Format
---------------

The data can be returned as JSON or as XML (or as a nice HTML page which by
default shows formatted JSON - handy for exploring the interface). You specify
which data format you want by using the "Accept" field in the header of
the HTTP GET request. For example, using ``curl`` you would do

    ``curl -X GET -H "Accept: application/json" http://api.ids.ac.uk/openapi/documents/1234/short``

More about XML formats, Dublin Core etc.

Contents of formats
-------------------

The **id only format** actually has two entries per item returned:

:id:    The asset_id
:metadata_url:   The url to get the full metadata for that asset. It will have a
        "friendly" format - that is the asset type (documents/themes/etc)
        will appear in the URL, it will use the "full" format, and after the
        "full" there will be a text representation of the title of the asset.

The **short format** has four entries per item returned:

:id:          As above.
:object_type: The type of the object
:title:       The full title of the asset
:metadata_url:         As above.

The **full format** has every field available for each item returned. These
include lots of things ...

Example Responses
-----------------

*(Note that all the below examples are nicely formatted, the actual format will
not have the whitespace.)*

In response to ``/openapi/documents/12345/short`` with ``Accept: application/json`` we get::

  [
    {
      "id": "12345", 
      "object_type": "CDocument", 
      "title": "Sharing knowledge for community development and transformation: a handbook", 
      "metadata_url": "http://api.ids.ac.uk/openapi/assets/12345/short"
    }
  ]

The same query with ``Accept: application/xml`` gives::

  <root>
    <list-item>
      <metadata_url>http://api.ids.ac.uk/openapi/assets/12345/short</metadata_url>
      <object_type>CDocument</object_type>
      <id>12345</id>
      <title>
        Sharing knowledge for community development and transformation: a handbook
      </title>
    </list-item>
  </root>

Multiple items look pretty similar.
