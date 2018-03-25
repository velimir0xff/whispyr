# -*- coding: utf-8 -*-

"""Fixtures for `whispyr` tests"""

import base64
import os
import pytest
import prettyserializer
import itertools
import functools

from collections import ByteString
from vcr import VCR
from whispyr import Whispir


TEST_USERNAME = 'U53RN4M3'
TEST_PASSWORD = 'P4ZZW0RD'
TEST_API_KEY = 'V4L1D4P1K3Y'


@pytest.fixture
def whispir(pytestconfig):
    username = pytestconfig.getoption('--whispir-username')
    password = pytestconfig.getoption('--whispir-password')
    api_key = pytestconfig.getoption('--whispir-api-key')
    return Whispir(username, password, api_key)


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
    options = {
        'record_mode': mode,
        'filter_headers': [
            ('authorization', replace_auth),
            ('set-cookie', None),
            ('cookie', None)
        ],
        'filter_query_parameters': [('apikey', TEST_API_KEY)],
        'before_record_response': scrub_patterns(
            ((api_key, TEST_API_KEY), (username, TEST_USERNAME))
        ),
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

    def before_record_response(response):
        if 'Set-Cookie' in response['headers']:
            del response['headers']['Set-Cookie']

        headers = response['headers']
        response['headers'] = {
            name: scrub_them_all(values) for name, values in headers.items()
        }
        response['body']['string'] = scrub_it(response['body']['string'])
        return response
    return before_record_response


def scrub_patterns(patches):
    pipeline = itertools.starmap(scrub_pattern, patches)
    return compose(pipeline)


def compose(functions):
    def compose_impl(f, g):
        return lambda x: f(g(x))
    return functools.reduce(compose_impl, functions, lambda x: x)


def replace(string, pattern, replacement):
    if isinstance(string, ByteString):
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
    parser.addoption('--vcr-mode', default='once',
                     choices=['once', 'new_episodes', 'none', 'all'],
                     help='Set VCR mode')
