# -*- coding: utf-8 -*-

"""Main module."""

from . import __version__

from collections import UserDict

from requests import Session
from requests.adapters import HTTPAdapter
from requests.auth import HTTPBasicAuth, AuthBase

from urllib.parse import urljoin, urlparse, parse_qsl

from urllib3.util import Retry
from urllib3.exceptions import MaxRetryError

WHISPIR_BASE_URL = 'https://api.whispir.com'


class WhispirError(Exception):

    def __init__(self, response):
        super().__init__()
        self.response = response


class ClientError(WhispirError):
    pass


class ServerError(WhispirError):
    pass


class JSONDecodeError(WhispirError):
    pass


class WhispirAuth(AuthBase):

    def __init__(self, api_key, username, password):
        self._api_key = api_key
        self._basic_auth = HTTPBasicAuth(username, password)

    def __call__(self, request):
        new_req = self._basic_auth(request)
        new_req.prepare_url(new_req.url, {'apikey': self._api_key})
        return new_req


class WhispirRetry(Retry):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.RETRY_AFTER_STATUS_CODES = frozenset([403, 413, 429, 503])
        self.raise_on_status = False
        self.raise_on_redirect = False

    def _is_method_retryable(self, method):
        return True

    def increment(self, method=None, url=None, response=None, error=None,
                  _pool=None, _stacktrace=None):
        if response:
            mashery_error = response.getheader("X-Mashery-Error-Code")
            if mashery_error == 'ERR_403_DEVELOPER_OVER_QPD':
                raise MaxRetryError(_pool, url, error)
        return super().increment(
            method=method, url=url, response=response, error=error,
            _pool=_pool, _stacktrace=_stacktrace)


DEFAULT_RETRY = WhispirRetry()


class Whispir:

    def __init__(self, username, password, api_key,
                 base_url=WHISPIR_BASE_URL, page_size=20, retry=DEFAULT_RETRY):
        self._base_url = base_url
        self.page_size = page_size
        self._session = Session()
        self._session.auth = WhispirAuth(api_key, username, password)
        adapter = HTTPAdapter(max_retries=retry)
        self._session.mount('http://', adapter)
        self._session.mount('https://', adapter)
        self._session.headers.update({
            'User-Agent': 'whispyr/{}'.format(__version__)
        })
        # collections
        self.workspaces = Workspaces(self)
        self.messages = Messages(self)
        self.templates = Templates(self)
        self.response_rules = ResponseRules(self)
        self.contacts = Contacts(self)
        self.apps = Apps(self)

    def request(self, method, path, **kwargs):
        url = urljoin(self._base_url, path)
        response = self._session.request(method, url, **kwargs)
        if response.ok:
            return self._maybe_return_json(response)
        else:
            if 400 <= response.status_code < 500:
                error = ClientError
            elif 500 <= self.status_code < 600:
                error = ServerError

            raise error(response)

    def _maybe_return_json(self, response):
        if not response.content:
            return

        try:
            return response.json()
        except ValueError:
            raise JSONDecodeError(response)


class Collection:

    def __init__(self, whispir, base_container=None):
        self.whispir = whispir
        class_name = self.__class__.__name__
        self.name = (getattr(self, 'name', False) or class_name.lower())
        type_name = (getattr(self, 'type_name', False) or
                     _singularize(self.name))
        self.vnd_type = 'application/vnd.whispir.{}-v1+json'.format(type_name)
        self.list_name = getattr(self, 'list_name', self.name)
        self.container = (getattr(self, 'container', False) or
                          globals()[_singularize(class_name)])
        self.resource = (getattr(self, 'resource', False) or self.name)
        self.base_container = base_container

        class ContainerProxy(self.container):
            collection = self
            container = self.container

            def __new__(self, *args, **kwargs):
                return self.container(self.collection, *args, **kwargs)

        setattr(self, self.container.__name__, ContainerProxy)

    def path(self, id=None):
        path = self.resource
        if id:
            path = '{}/{}'.format(path, id)

        if self.base_container:
            path = '{}/{}'.format(self.base_container.path(), path)

        return path

    def request(self, method, path, headers=None, **kwargs):
        headers = kwargs.pop('headers', {})
        collection_type = self.vnd_type
        headers.update({
            'Content-Type': collection_type,
            'Accept': collection_type
        })
        return self.whispir.request(method, path, headers=headers, **kwargs)

    def _containerize(self, item):
        return self.container(self, **item)

    def create(self, **kwargs):
        path = self.path()
        item = self.request('post', path, json=kwargs)
        return self._containerize(item)

    def show(self, id):
        path = self.path(id)
        item = self.request('get', path)
        return self._containerize(item)

    def _get_page(self, path, **kwargs):
        result = self._try_get(path, kwargs)
        return self._page_items(result)

    def _page_items(self, response):
        return response.get(self.list_name, [])

    def list(self, **kwargs):
        path = self.path()

        list_items = self._list
        if 'offset' in kwargs or 'limit' in kwargs:
            list_items = self._get_page

        for item in list_items(path, **kwargs):
            yield self._containerize(item)

    def _list(self, path, **kwargs):
        kwargs['limit'] = self.whispir.page_size
        kwargs['offset'] = 0

        while True:
            result = self._try_get(path, kwargs)
            items = self._page_items(result)
            for item in items:
                yield item

            links = result.get('link', [])
            link = _find_link(links, 'next')
            if not link:
                return

            uri = urlparse(link['uri'])
            query = dict(parse_qsl(uri.query))
            kwargs['limit'] = query['limit']
            kwargs['offset'] = query['offset']

    def _try_get(self, path, params):
        try:
            return self.request('get', path, params=params)
        except (ClientError, JSONDecodeError) as e:
            if e.response.status_code == 404:
                return {}
            raise

    def update(self, id, **kwargs):
        path = self.path(id)
        self.request('put', path, json=kwargs)

    def delete(self, id):
        path = self.path(id)
        self.request('delete', path)


class Nonpaginatable:

    def _list(self, path, **kwargs):
        return self._get_page(path, **kwargs)


class Streamable:

    def _list(self, path, **kwargs):
        limit = self.whispir.page_size
        kwargs['limit'] = limit
        kwargs['offset'] = 0

        while True:
            item = None
            for item in self._get_page(path, **kwargs):
                yield item

            if not item:
                break

            kwargs['offset'] += limit


class Container(UserDict):

    def __init__(self, collection, id=None, **kwargs):
        self.collection = collection
        self.whispir = collection.whispir

        if not id:
            id = self.id_from_links(kwargs.get('link', []))

        if id:
            kwargs['id'] = id

        super().__init__(kwargs)

    @classmethod
    def id_from_links(cls, links):
        link = _find_link(links, 'self')
        if link:
            return cls.id_from_uri(link['uri'])

    @staticmethod
    def id_from_uri(url):
        path = urlparse(url).path
        return path.split('/')[-1]

    def path(self):
        return self.collection.path(self.id())

    def id(self):
        return self['id']


class Workspaces(Nonpaginatable, Collection):
    pass


class Messages(Streamable, Collection):

    def create(self, **kwargs):
        try:
            super().create(**kwargs)
        except JSONDecodeError as e:
            headers = e.response.headers
            msg_id = self.Message.id_from_uri(headers['location'])

        return self.Message(id=msg_id)

    send = create


class MessageStatuses(Collection):

    list_name = 'messageStatuses'
    resource = 'messagestatus'


class MessageResponses(Collection):
    pass


class Templates(Collection):
    list_name = 'messagetemplates'


class ResponseRules(Nonpaginatable, Collection):
    list_name = 'responseRules'


class Contacts(Collection):
    pass


class Apps(Collection):
    list_name = 'applications'


class Workspace(Container):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.messages = Messages(self.whispir, self)
        self.templates = Templates(self.whispir, self)
        self.response_rules = ResponseRules(self.whispir, self)
        self.contacts = Contacts(self.whispir, self)
        self.apps = Apps(self.whispir, self)


class Message(Container):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.statuses = MessageStatuses(self.whispir, self)
        self.responses = MessageResponses(self.whispir, self)


class MessageStatus(Container):
    pass


class MessageResponse(Container):
    pass


class Template(Container):
    pass


class ResponseRule(Container):
    pass


class Contact(Container):
    pass


class App(Container):
    pass


def _singularize(string):
    rules = {'ies': 'y', 'uses': 'us', 's': ''}
    for suffix, replacement in rules.items():
        if string.endswith(suffix):
            return string[:-len(suffix)] + replacement

    return string


def _find_link(links, relation, default=None):
    def is_relation(it):
        return it['rel'] == relation
    return next((it for it in links if is_relation(it)), default)
