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

Single Asset Response Format
----------------------------

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

Search/All Response Format
--------------------------

At the top level, the response has two entries - **metadata** and **results**. 

The **metadata** section can contain:

* **num_results** - the total number of results for that search.
* **start_offset** - the offset into the results of the items in the **results** section.
* **next_page** - a link to the next page of results (only present if there are more results after this page).
* **prev_page** - a link to the previous page of results (only present if there are more results before this page).

The **results** section is a list of results. Each item has data as specified
by the format part of the URL, as for the single asset response.

The exception to all this is that if the **num_results_only** query parameter
is present, then the response will only have the metadata section, and that
will only have the **num_results** item present. The nesting of data will be
the same as for the full response though, allowing the same code to be used in
both cases.

Field List Response Format
--------------------------

This is just a list of the names of the fields present.

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
