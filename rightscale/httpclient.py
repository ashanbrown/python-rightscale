from functools import partial
import requests


DEFAULT_ROOT_RES_PATH = '/'


class HTTPClient(object):

    """
    Convenience wrapper around Requests.

    :param str endpoint: URL for the API endpoint. E.g. ``https://blah.org``.

    :param str root_path: The initial path to use for discovering the rest of
        the resources.  E.g. ``/api/``.

    :param dict extra_headers: When specified, these key-value pairs are added
        to the default HTTP headers passed in with each request.

    """

    def __init__(
            self,
            endpoint='',
            root_path=DEFAULT_ROOT_RES_PATH,
            extra_headers=None,
            ):
        self.endpoint = endpoint
        self.root_path = root_path
        s = requests.Session()
        s.headers['Accept'] = 'application/json'
        if extra_headers:
            s.headers.update(extra_headers)
        self.s = s

        # convenience methods
        self.delete = partial(self.request, 'delete')
        self.get = partial(self.request, 'get')
        self.head = partial(self.request, 'head')
        self.post = partial(self.request, 'post')
        self.put = partial(self.request, 'put')

        self.reset_cache()

    def request(self, method, path='/', url=None, ignore_codes=[], **kwargs):
        """
        Performs HTTP request.

        :param str method: An HTTP method (e.g. 'get', 'post', 'PUT', etc...)

        :param str path: A path component of the target URL.  This will be
            appended to the value of ``self.endpoint``.  If both :attr:`path`
            and :attr:`url` are specified, the value in :attr:`url` is used and
            the :attr:`path` is ignored.

        :param str url: The target URL (e.g.  ``http://server.tld/somepath/``).
            If both :attr:`path` and :attr:`url` are specified, the value in
            :attr:`url` is used and the :attr:`path` is ignored.

        :param ignore_codes: List of HTTP error codes (e.g.  404, 500) that
            should be ignored.  If an HTTP error occurs and it is *not* in
            :attr:`ignore_codes`, then an exception is raised.
        :type ignore_codes: list of int

        :param kwargs: Any other kwargs to pass to :meth:`requests.request()`.

        Returns a :class:`requests.Response` object.
        """
        _url = url if url else (self.endpoint + path)
        r = self.s.request(method, _url, **kwargs)
        if not r.ok and r.status_code not in ignore_codes:
            r.raise_for_status()
        return r

    def reset_cache(self):
        self._root_response = None

    @property
    def root_response(self):
        if self._root_response is None:
            try:
                self._root_response = self.get(self.root_path).json()
            except:
                return {}
        return self._root_response
