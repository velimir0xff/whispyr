# -*- coding: utf-8 -*-

"""Tests for `whispyr` package"""

import pytest
import httpretty

import whispyr

import base64
from urllib.parse import urlencode, urlparse, parse_qs


TEST_USERNAME = 'U53RN4M3'
TEST_PASSWORD = 'P4ZZW0RD'
TEST_API_KEY = 'V4L1D4P1K3Y'
TEST_WORKSPACE = 'W0RK5P4C3'

httpretty.HTTPretty.allow_net_connect = False


def test_version():
    assert whispyr.__version__ == '0.1.0'


@pytest.fixture
def whispir():
    return whispyr.Whispir(
        username=TEST_USERNAME,
        password=TEST_PASSWORD,
        api_key=TEST_API_KEY)


@httpretty.activate
def test_basic_auth_and_api_key_provided(whispir):
    base_url = whispyr.whispyr.WHISPIR_BASE_URL
    url = _mkurl(base_url, 'fake')
    httpretty.register_uri(httpretty.GET, url, body='{}')
    whispir.request('get', 'fake')
    assert httpretty.has_request()
    request = httpretty.last_request()
    assert 'Authorization' in request.headers
    request.headers['Authorization']
    basic_auth = request.headers['Authorization']
    expected_basic = _basic_auth(TEST_USERNAME, TEST_PASSWORD)
    assert basic_auth == expected_basic
    assert 'apikey' in request.querystring
    api_key = request.querystring['apikey'][0]
    assert api_key == TEST_API_KEY


@httpretty.activate
def test_messages_create(whispir):
    base_url = whispyr.whispyr.WHISPIR_BASE_URL
    url = _mkurl(base_url, 'workspaces', TEST_WORKSPACE, 'messages')
    msg_id = '9723ABB5948B9AF2'
    location = _mkurl(url, msg_id, apikey=TEST_API_KEY)
    httpretty.register_uri(
        httpretty.POST,
        url,
        status=202,
        body='Your request has been accepted for processing',
        location=location
    )
    workspace = whispir.workspaces.Workspace(id=TEST_WORKSPACE)
    workspace.messages.create(
        to='+441171024524', subject='foo', body='bar')

    assert httpretty.has_request()
    request = httpretty.last_request()
    assert request.method == 'POST'


def _mkurl(*parts, **kwargs):
    url = '/'.join(parts)
    query = urlencode(kwargs)
    return '{}?{}'.format(url, query)


def _basic_auth(username, password):
    username = username.encode('latin1')
    password = password.encode('latin1')
    b64auth = base64.b64encode(b':'.join((username, password)))
    return 'Basic {}'.format(b64auth.decode('utf-8'))
