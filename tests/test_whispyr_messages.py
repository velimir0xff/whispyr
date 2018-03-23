# -*- coding: utf-8 -*-


"""Tests for `whispyr` package"""

from collections import Iterable, MutableMapping
from urllib.parse import urlparse

from whispyr import MessageStatus


def test_messages_create(whispir, cassette):
    workspace = whispir.workspaces.Workspace(id='8080DE5434485ED4')
    message = workspace.messages.create(
        to='success@simulator.amazonses.com',
        subject='whispyr test',
        body='test message, please disregard')
    _check_message_created(message, cassette)


def test_send_message_for_root_workspace(whispir, cassette):
    message = whispir.messages.create(
        to='success@simulator.amazonses.com',
        subject='whispyr test',
        body='test message, please disregard')
    _check_message_created(message, cassette)


def test_send_alias_creates_message(whispir, cassette):
    message = whispir.messages.send(
        to='success@simulator.amazonses.com',
        subject='whispyr test',
        body='test message, please disregard')
    _check_message_created(message, cassette)


def test_show_message(whispir, cassette):
    workspace = whispir.workspaces.Workspace(id='8080DE5434485ED4')
    message = workspace.messages.show('E9A5630CECBC7EB7')
    _check_shown_message(message)


def test_show_message_from_root_workspace(whispir, cassette):
    message = whispir.messages.show('E9A5630CECBC7EB7')
    _check_shown_message(message)


def test_show_message_statuses(whispir, cassette):
    workspace = whispir.workspaces.Workspace(id='8080DE5434485ED4')
    message = workspace.messages.Message(id='E9A5630CECBC7EB7')
    statuses = message.statuses.list()
    assert isinstance(statuses, Iterable)
    statuses = list(statuses)
    assert len(statuses) > 0
    for status in statuses:
        assert isinstance(status, MessageStatus)
        assert 'categories' in status


def test_show_detailed_statuses(whispir, cassette):
    workspace = whispir.workspaces.Workspace(id='8080DE5434485ED4')
    message = workspace.messages.Message(id='9F148597C9CB1B2F')
    statuses = message.statuses.detailed_list()
    assert isinstance(statuses, Iterable)
    statuses = list(statuses)
    assert len(statuses) > 0
    for status in statuses:
        assert isinstance(status, MessageStatus)
        assert 'status' in status


def _check_shown_message(message):
    assert isinstance(message, MutableMapping)
    assert 'id' in message
    assert 'subject' in message


def test_list_messages_for_root_workspace(whispir, cassette):
    messages = whispir.messages.list()
    _check_list_messages(messages)


def test_list_messages(whispir, cassette):
    workspace = whispir.workspaces.Workspace(id='8080DE5434485ED4')
    messages = workspace.messages.list()
    _check_list_messages(messages)


def _check_list_messages(messages):
    assert isinstance(messages, Iterable)
    messages = list(messages)
    assert len(messages) > 0
    for message in messages:
        assert isinstance(message, MutableMapping)
        assert 'id' in message
        assert 'subject' in message


def _check_message_created(message, cassette):
    assert len(cassette) == 1
    location = cassette.responses[0]['headers']['Location'][0]
    assert message['id'] == _msg_location(location)


def _msg_location(url):
    path = urlparse(url).path
    return path.split('/')[-1]
