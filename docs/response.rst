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
