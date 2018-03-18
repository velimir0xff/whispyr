# -*- coding: utf-8 -*-

"""Main module."""

from . import __version__

from requests import Session
from requests.auth import HTTPBasicAuth, AuthBase

from urllib.parse import urljoin

WHISPIR_BASE_URL = 'https://api.whispir.com'


class WhispirError(Exception):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class WhispirAuth(AuthBase):

    def __init__(self, api_key, username, password):
        self._api_key = api_key
        self._basic_auth = HTTPBasicAuth(username, password)

    def __call__(self, request):
        new_req = self._basic_auth(request)
        new_req.prepare_url(new_req.url, {'apikey': self._api_key})
        return new_req


class Whispir:

    def __init__(self, username, password, api_key,
                 workspace=None, base_url=WHISPIR_BASE_URL):
        self.workspace = workspace
        self._base_url = base_url
        self._session = Session()
        self._session.auth = WhispirAuth(api_key, username, password)
        self._session.headers.update({
            'User-Agent': 'whispyr/{}'.format(__version__)
        })
        self.messages = Messages(self)

    def request(self, method, path, **kwargs):
        url = urljoin(self._base_url, path)
        response = self._session.request(method, url, **kwargs)
        try:
            return response.json()
        except ValueError:
            return '{}: {}'.format(response.status_code, response.text)


class Collection:

    def __init__(self, whispir):
        self.whispir = whispir
        self.name = (getattr(self, 'name', False) or
                     self.__class__.__name__.lower())
        type_name = getattr(self, 'type_name', False) or _singularize(self.name)
        self.type = f'application/vnd.whispir.{type_name}-v1+json'

    @property
    def path(self):
        workspace = self.whispir.workspace
        return '/workspaces/{}/{}'.format(workspace, self.name)

    def request(self, method, path, headers=None, **kwargs):
        headers = kwargs.pop('headers', {})
        collection_type = self.type
        headers.update({
            'Content-Type': collection_type,
            'Accept': collection_type
        })
        return self.whispir.request(method, path, headers=headers, **kwargs)

    def create(self, **kwargs):
        path = self.path
        self.request('post', path, json=kwargs)


class Messages(Collection):
    pass


def _singularize(string):
    rules = {'ies': 'y', 's': ''}
    for suffix, replacement in rules.items():
        if string.endswith(suffix):
            return string[:-len(suffix)] + replacement

    return string
