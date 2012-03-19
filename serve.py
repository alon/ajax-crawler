"""
Implement the ajax crawling API by google:
    https://developers.google.com/webmasters/ajax-crawling/docs/specification

Usage:
    1. Put a frontend that filters all urls containing _escaped_fragment_ to this server.
    2. Run this server

Todo:
    Caching.

"""

import os
import dircache
import sys

try:
    from flask import Flask, request
except ImportError:
    print "missing flask, please install"
    sys.exit(-1)

def which(f):
    for p in os.environ['PATH'].split(':'):
        if f in dircache.listdir(p):
            return os.path.join(p, f)
    return None

def require(exe):
    if not which(exe):
        print "missing %s" % exe
        sys.exit(-1)

require("phantomjs")
require("casperjs")

from getpage import getpage
from urlparse import unquote, urlparse, urlunparse, ParseResult

app = Flask(__name__)

def unescape_ajax_request(url):
    """
    ?_escaped_fragment_=key1=value1%26key2=value2

    ^
    |
    V

    #!key1=value1&key2=value2

    Remove from the URL all tokens beginning with _escaped_fragment_= (Note especially that the = must be removed as well).
    Remove from the URL the trailing ? or & (depending on whether the URL had query parameters other than _escaped_fragment_).
    Add to the URL the tokens #!.
    Add to the URL all tokens after _escaped_fragment_= after unescaping them.
    """
    parsed = urlparse(url)
    query = []
    for token in parsed.query.split('&'):
        if token.startswith('_escaped_fragment_='):
            _dump_, fragment_params = token.split('_escaped_fragment_=')
            fragment = '!' + unquote(fragment_params)
    query = '&'.join(query)
    return urlunparse(ParseResult(scheme=parsed.scheme,
        netloc=parsed.netloc, path=parsed.path, params=parsed.params, query=query,
        fragment=fragment))

# https://developers.google.com/webmasters/ajax-crawling/docs/specification
# %00..20
# %23
# %25..26
# %2B
# %7F..FF
convert = {}
for start, _end in [(00, 0x20), (0x23, 0x23), (0x25, 0x26), (0x2b, 0x2b), (0x7f, 0xff)]:
    for c in xrange(start, _end + 1):
        convert[chr(c)] = '%%%x' % c

def escape_ajax_request(url):
    """
    The hash fragment becomes part of the query parameters.
    The hash fragment is indicated in the query parameters by preceding it with _escaped_fragment_=
    Some characters are escaped when the hash fragment becomes part of the query parameters. These characters are listed below.
    All other parts of the URL (host, port, path, existing query parameters, and so on) remain unchanged.
    """
    parsed = urlparse(url)
    fragment = parsed.fragment[1:] # remove '!'
    orig_query = parsed.query
    escaped = '_escaped_fragment_=' + ''.join(convert.get(c, c) for c in fragment)
    if orig_query:
        query = orig_query + '&' + escaped
    else:
        query = escaped
    return urlunparse(ParseResult(scheme=parsed.scheme,
        netloc=parsed.netloc, path=parsed.path, params=parsed.params, query=query,
        fragment=''))

# slight abuse of errorhandler as a catchall url handler, note the ,200 at
# the normal return
@app.errorhandler(404)
def handle_static_request(*args):
    # verify this is actually a correct request
    if not '?_escaped_fragment_=' in request.path:
        return "<html><body>your frontend is misconfigured, it is pointing a normal url to this ajax-crawler backend</body></html>", 500
    url = unescape_ajax_request(request.path)
    # TODO: cache me
    output = getpage(url)
    return output, 200

if __name__ == '__main__':
    app.run(port=8888)
