# -*- coding: utf-8 -*-

"""Main module."""

from . import __version__

import collections

from requests import Session
from requests.auth import HTTPBasicAuth, AuthBase

from urllib.parse import urljoin, urlparse


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


class Whispir:

    def __init__(self, username, password, api_key, base_url=WHISPIR_BASE_URL):
        self._base_url = base_url
        self._session = Session()
        self._session.auth = WhispirAuth(api_key, username, password)
        self._session.headers.update({
            'User-Agent': 'whispyr/{}'.format(__version__)
        })
        # collections
        self.messages = Messages(self)
        self.workspaces = Workspaces(self)

    def request(self, method, path, **kwargs):
        url = urljoin(self._base_url, path)
        response = self._session.request(method, url, **kwargs)
        if response.ok:
            try:
                return response.json()
            except ValueError:
                raise JSONDecodeError(response)
        else:
            if 400 <= response.status_code < 500:
                error = ClientError
            elif 500 <= self.status_code < 600:
                error = ServerError

            raise error(response)


class ContainerProxyMeta(type):

    def __new__(mcl, name, bases, nmspc):
        container = nmspc['container']
        prefix = container.__class__.__name__.capitalize()
        name = prefix + 'Proxy'
        return super(ContainerProxyMeta, mcl).__new__(mcl, name, bases, nmspc)


class Collection:

    def __init__(self, whispir, base_container=None):
        self.whispir = whispir
        self.name = (getattr(self, 'name', False) or
                     self.__class__.__name__.lower())
        type_name = (getattr(self, 'type_name', False) or
                     _singularize(self.name))
        self.vnd_type = 'application/vnd.whispir.{}-v1+json'.format(type_name)
        self.container = (getattr(self, "container", False) or
                          globals()[type_name.capitalize()])
        self.base_container = base_container

        class ContainerProxy(metaclass=ContainerProxyMeta):
            collection = self
            container = self.container

            def __new__(self, *args, **kwargs):
                return self.container(self.collection, *args, **kwargs)

        setattr(self, self.container.__name__, ContainerProxy)

    def path(self, id=None):
        path = self.name
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

    def create(self, **kwargs):
        path = self.path()
        response = self.request('post', path, json=kwargs)
        return self.container(self, **response.json())


class Container(collections.UserDict):

    def __init__(self, collection, **kwargs):
        self.collection = collection
        self.whispir = collection.whispir
        super().__init__(kwargs)

    def path(self):
        return self.collection.path(self.id())

    def id(self):
        return self['id']


class Workspaces(Collection):
    pass


class Messages(Collection):

    def create(self, **kwargs):
        try:
            super().create(**kwargs)
        except JSONDecodeError as e:
            headers = e.response.headers
            msg_id = self.__message_id_from_url(headers['location'])

        return self.Message(id=msg_id)

    send = create

    @staticmethod
    def __message_id_from_url(url):
        path = urlparse(url).path
        return path.split('/')[-1]


class Workspace(Container):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.messages = Messages(self.whispir, self)


class Message(Container):
    pass


def _singularize(string):
    rules = {'ies': 'y', 's': ''}
    for suffix, replacement in rules.items():
        if string.endswith(suffix):
            return string[:-len(suffix)] + replacement

    return string
