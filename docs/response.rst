================
Response Details
================

Response Format
===============

The data can be returned as JSON or as XML (or as a nice HTML page which by
default shows formatted JSON - handy for exploring the interface). You specify
which data format you want by using the "Accept" field in the header of
the HTTP GET request. For example, using ``curl`` you would do::

    ``curl -X GET -H "Accept: application/json" -H "Token-Guid: 9827f62a-8bbc-4d22-96b4-771d08859926" http://api.ids.ac.uk/openapi/documents/A12345/short``

Single Object Response Format
-----------------------------

The **id only format** actually has two entries per object returned:

:object_id: The object_id. This is a letter followed by digits. The letter
        indicates whether this object is an Asset or a Category.
:metadata_url:   The url to get the full metadata for that object. It will have a
        "friendly" format - that is the object type (documents/themes/etc)
        will appear in the URL, it will use the "full" format, and after the
        "full" there will be a text representation of the title of the object.

The **short format** has four entries per item returned:

:object_id:      As above.
:object_type:    The type of the object
:title:          The full title of the object
:metadata_url:   As above.

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
by the format part of the URL, as for the single object response.

The exception to all this is that if the **num_results_only** query parameter
is present, then the response will only have the metadata section, and that
will only have the **num_results** item present. The nesting of data will be
the same as for the full response though, allowing the same code to be used in
both cases.

Field List Response Format
--------------------------

This is just a list of the names of the fields present. For a full list, see
:doc:`available_fields`.

Category Count Response Format
------------------------------

This will have a metadata section, giving the total number of results for the query,
and a xxx_count section which will be a list of lists - each list will have two
items. The first item will be the name of the category and the second
item will be the number of times the category appears in the results.

Example Responses
=================

*(Note that all the below examples are nicely formatted, the actual response will
not have the whitespace, unless you are using the web interface.)*

In response to ``/openapi/documents/A12345/short`` with ``Accept: application/json`` we get::

  [
    {
      "object_id": "A12345", 
      "object_type": "CDocument", 
      "title": "Sharing knowledge for community development and transformation: a handbook", 
      "metadata_url": "http://api.ids.ac.uk/openapi/objects/A12345/short"
    }
  ]

The same query with ``Accept: application/xml`` gives::

  <root>
    <list-item>
      <metadata_url>http://api.ids.ac.uk/openapi/objects/A12345/short</metadata_url>
      <object_type>CDocument</object_type>
      <object_id>A12345</object_id>
      <title>
        Sharing knowledge for community development and transformation: a handbook
      </title>
    </list-item>
  </root>

Multiple items look pretty similar.
