=============
Authorisation
=============

Before you can do anything with the API you will have to be authorised with the
API service. First you will have to sign up - do that by going to
http://api.ids.ac.uk/accounts/register/ The system will send you an email with
a link you need to follow, and then you need to fill in your profile, including
agreeing to the Terms and Conditions that cover usage of the API.

Once you are logged in you can browse around the site in your web browser -
start at http://api.ids.ac.uk/openapi/ - and have a play. Your browser will
handle the cookies for you, so nothing more is required at that point, while
trying out the API.

However you probably don't want to do a full login and handle cookies in your
code that uses the API. So instead you can use a generated token that is
associated with your account. You can get your token by going to
http://api.ids.ac.uk/profiles/view/

Once you have your token, tell your code to add it to the headers as
"Token-Guid". So using curl, you could do::

    curl -X GET -H "Accept: application/json" -H "Token-Guid: 9827f62a-8bbc-4d22-96b4-771d08859926" http://api.ids.ac.uk/openapi/documents/A12345/short

Alternatively, to have a play in a web browser, you can add the token to the
URL as the query parameter ``_token_guid``, for example::

    http://api.ids.ac.uk/openapi/documents/search?q=undp&_token_guid=9827f62a-8bbc-4d22-96b4-771d08859926

User Levels
===========

By default you will be limited to a subset of the full field list, and
relatively few calls per hour. If you want to get a higher level of access you
will have to contact IDS - api@ids.ac.uk *(email address to be confirmed)*.
