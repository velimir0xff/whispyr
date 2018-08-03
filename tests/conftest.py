# -*- coding: utf-8 -*-

"""Fixtures for `whispyr` tests"""

import base64
import os
import pytest
import prettyserializer
import itertools
import functools
import uuid
import random
import hashlib

from six import binary_type

from vcr import VCR
from vcr.request import Request
from vcr.util import CaseInsensitiveDict

from whispyr import Whispir

try:
    from functools import singledispatch
except ImportError:
    from singledispatch import singledispatch


TEST_USERNAME = 'U53RN4M3'
TEST_PASSWORD = 'P4ZZW0RD'
TEST_API_KEY = 'V4L1D4P1K3Y'
TEST_GCM_API_KEY = '9OO9l3ClouDm355491n94P1K3y'


@pytest.fixture
def whispir(pytestconfig):
    username = pytestconfig.getoption('--whispir-username')
    password = pytestconfig.getoption('--whispir-password')
    api_key = pytestconfig.getoption('--whispir-api-key')
    return Whispir(username, password, api_key)


@pytest.fixture
def gcm_api_key(pytestconfig):
    return pytestconfig.getoption('--whispir-gcm-api-key')


@pytest.fixture
def cassette(request, pytestconfig):
    cassette_library_dir = cassettes_dir(request)
    vcr = make_vcr(pytestconfig, cassette_library_dir)
    path = request.function.__name__
    with vcr.use_cassette(path) as cass:
        yield cass


def make_vcr(pytestconfig, cassette_library_dir):
    mode = pytestconfig.getoption('--vcr-mode')
    api_key = pytestconfig.getoption('--whispir-api-key')
    username = pytestconfig.getoption('--whispir-username')
    gcm_api_key = pytestconfig.getoption('--whispir-gcm-api-key')
    scrubber = scrub_patterns(((api_key, TEST_API_KEY),
                               (username, TEST_USERNAME),
                               (gcm_api_key, TEST_GCM_API_KEY)))
    options = {
        'record_mode': mode,
        'filter_headers': [
            ('authorization', replace_auth),
            ('set-cookie', None),
            ('cookie', None)
        ],
        'filter_query_parameters': [('apikey', TEST_API_KEY)],
        'before_record_response': scrubber,
        'before_record_request': scrubber,
        'path_transformer': VCR.ensure_suffix('.yaml'),
        'decode_compressed_response': True,
        'cassette_library_dir': cassette_library_dir,
        'match_on': (
            'method', 'scheme', 'host', 'port', 'path', 'query', 'headers'
        ),
        'serializer': 'pretty-yaml'
    }
    vcr = VCR(**options)
    vcr.register_serializer('pretty-yaml', prettyserializer)
    return vcr


def recorded_fixture(name=None, library_dir='tests/cassettes/fixtures'):
    def decorator(fixture):
        path = name or fixture.__name__

        @pytest.fixture(name=fixture.__name__)
        # TODO: figure out required fixtures from decorated function
        def wrapper(pytestconfig, whispir):
            vcr = make_vcr(pytestconfig, library_dir)
            with vcr.use_cassette(path):
                return fixture(whispir)
        return wrapper

    return decorator


@recorded_fixture()
def workspace(whispir):
    project_name = 'whispyr tests'
    for workspace in whispir.workspaces.list():
        if workspace['projectName'] == project_name:
            return workspace

    workspace = whispir.workspaces.create(projectName=project_name, status='A')
    return whispir.workspaces.show(workspace['id'])


@pytest.fixture(params=[False])
def app(request, whispir, workspace, gcm_api_key, cassette):
    delete = request.param
    return _create_fixture_app(
        request, whispir.apps, workspace, gcm_api_key, delete=delete)


@pytest.fixture(params=[2])
def apps(request, whispir, workspace, gcm_api_key, cassette):
    num = request.param
    return [_create_fixture_app(request, whispir.apps, workspace, gcm_api_key)
            for _ in range(num)]


def _create_fixture_app(request, apps, workspace, gcm_api_key, delete=True):
    name = hashlib.md5(str(uuid.uuid4()).encode('utf-8')).hexdigest()
    app = {
        'name': name,
        'description': 'App ({}) to test whispyr apps CRUD works'.format(name),
        'bundleId': '1',
        'options': {
            'workspaces': workspace['id'],
            'deviceLimit': 3,
            'apiKey': str(uuid.uuid4()),
            'clientSecret': str(uuid.uuid4())
        },
        'gcm': {
            'gcmProjectId': 'foobar-204e3',
            'gcmProjectNumber': 383181709987,
            'gcmApiKey': gcm_api_key
        },
        'registrationTypes': [
            'INVITE'
        ]
    }

    app = apps.create(**app)

    if delete:
        def _delete():
            apps.delete(app['id'])

        request.addfinalizer(_delete)

    return app


@pytest.fixture(params=[False])
def contact(request, workspace, cassette):
    delete = request.param
    return _create_fixture_contact(
        request, workspace.contacts, delete=delete)


@pytest.fixture(params=[True])
def generic_contact(request, whispir, cassette):
    delete = request.param
    return _create_fixture_contact(
        request, whispir.contacts, delete=delete)


@pytest.fixture(params=[2])
def contacts(request, workspace, cassette):
    num = request.param
    return [_create_fixture_contact(request, workspace.contacts)
            for _ in range(num)]


def _create_fixture_contact(request, contacts, delete=True):
    email = 'success+{}@simulator.amazonses.com'.format(uuid.uuid4())
    number = random.randrange(61420000000, 61430000000)
    contact = {
        'firstName': 'John',
        'lastName': 'Wick',
        'status': 'A',
        'timezone': 'Australia/Melbourne',
        'workEmailAddress1': email,
        'workMobilePhone1': str(number),
        'workCountry': 'Australia',
        'messagingoptions': [
            {
                'channel': 'sms',
                'enabled': 'true',
                'primary': 'WorkMobilePhone1'
            },
            {
                'channel': 'email',
                'enabled': 'true',
                'primary': 'WorkEmailAddress1'
            },
            {
                'channel': 'voice',
                'enabled': 'true',
                'primary': 'WorkMobilePhone1'
            }
        ]
    }

    contact = contacts.create(**contact)
    contact = contacts.show(contact['id'])

    if delete:
        def _delete():
            contacts.delete(contact['id'])

        request.addfinalizer(_delete)

    return contact


def replace_auth(key, value, request):
    username = TEST_USERNAME.encode('utf-8')
    password = TEST_PASSWORD.encode('utf-8')
    b64auth = base64.b64encode(b':'.join((username, password)))
    return 'Basic {}'.format(b64auth.decode('utf-8'))


def scrub_pattern(pattern, replacement=''):
    def scrub_it(string):
        return replace(string, pattern, replacement)

    def scrub_them_all(seq):
        return list(map(scrub_it, seq))

    @singledispatch
    def before_record(response):
        if 'Set-Cookie' in response['headers']:
            del response['headers']['Set-Cookie']

        headers = response['headers']
        response['headers'] = {
            name: scrub_them_all(values) for name, values in headers.items()
        }
        new_body = scrub_it(response['body']['string'])
        response['body']['string'] = new_body

        headers = CaseInsensitiveDict(response['headers'])
        if 'content-length' in headers:
            headers['content-length'] = [str(len(new_body))]
            response['headers'] = dict(headers)

        return response

    @before_record.register(Request)
    def _(request):
        orig_body = request.body
        if orig_body:
            new_body = scrub_it(orig_body)
            request.body = new_body
            headers = request.headers
            if 'content-length' in headers:
                headers['content-length'] = str(len(new_body))

        return request

    return before_record


def scrub_patterns(patches):
    pipeline = itertools.starmap(scrub_pattern, patches)
    return compose(pipeline)


def compose(functions):
    def compose_impl(f, g):
        return lambda x: f(g(x))
    return functools.reduce(compose_impl, functions, lambda x: x)


def replace(string, pattern, replacement):
    if isinstance(string, binary_type):
        pattern = pattern.encode('ascii')
        replacement = replacement.encode('ascii')
    return string.replace(pattern, replacement)


def cassettes_dir(request):
    return os.path.join(
        request.fspath.dirname,
        'cassettes',
        request.fspath.basename.replace('.py', ''))


def pytest_addoption(parser):
    parser.addoption('--whispir-username', default=TEST_USERNAME,
                     help='Whispir username')
    parser.addoption('--whispir-password', default=TEST_PASSWORD,
                     help='Whispir password')
    parser.addoption('--whispir-api-key', default=TEST_API_KEY,
                     help='Whispir API key')
    parser.addoption('--whispir-gcm-api-key', default=TEST_GCM_API_KEY,
                     help='Whispir Google Cloud Messaging API key')
    parser.addoption('--vcr-mode', default='once',
                     choices=['once', 'new_episodes', 'none', 'all'],
                     help='Set VCR mode')
