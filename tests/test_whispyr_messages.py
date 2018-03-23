# -*- coding: utf-8 -*-


"""Tests for `whispyr` package"""

from urllib.parse import urlparse


def test_messages_create(whispir, cassete):
    workspace = whispir.workspaces.Workspace(id='8080DE5434485ED4')
    message = workspace.messages.create(
        to='success@simulator.amazonses.com',
        subject='whispyr test',
        body='test message, please disregard')
    _check_message_created(message, cassete)


def test_send_message_for_root_workspace(whispir, cassete):
    message = whispir.messages.create(
        to='success@simulator.amazonses.com',
        subject='whispyr test',
        body='test message, please disregard')
    _check_message_created(message, cassete)


def test_send_alias_creates_message(whispir, cassete):
    message = whispir.messages.send(
        to='success@simulator.amazonses.com',
        subject='whispyr test',
        body='test message, please disregard')
    _check_message_created(message, cassete)


def _check_message_created(message, cassete):
    assert len(cassete) == 1
    location = cassete.responses[0]['headers']['Location'][0]
    assert message['id'] == _msg_location(location)


def _msg_location(url):
    path = urlparse(url).path
    return path.split('/')[-1]
