# -*- coding: utf-8 -*-


"""Tests for `whispyr` package"""

import itertools

from six.moves.urllib.parse import urlparse

from whispyr import Message, MessageStatus, MessageResponse


def test_messages_create(workspace, cassette):
    message = workspace.messages.create(
        to='success@simulator.amazonses.com',
        subject='whispyr test',
        body='test message, please disregard')
    _check_created_message(message, cassette)


def test_send_generic_message(whispir, cassette):
    message = whispir.messages.create(
        to='success@simulator.amazonses.com',
        subject='whispyr test',
        body='test message, please disregard')
    _check_created_message(message, cassette)


def test_send_alias_creates_message(workspace, cassette):
    message = workspace.messages.send(
        to='success@simulator.amazonses.com',
        subject='whispyr test',
        body='test message, please disregard')
    _check_created_message(message, cassette)


def test_show_message(workspace, cassette):
    _test_show_message(workspace.messages)


def test_show_generic_message(whispir, cassette):
    _test_show_message(whispir.messages)


def _test_show_message(messages):
    message = next(messages.list())
    message = messages.show(message['id'])
    _check_message(message)


def test_list_message_statuses(workspace, cassette):
    # message ID here is explicitly specified as it's easier than to
    # send a response back from test
    message = workspace.messages.Message(id='09CD9065116DF39F')
    statuses = message.statuses.list()
    statuses = list(statuses)
    assert len(statuses) > 0
    for status in statuses:
        assert isinstance(status, MessageStatus)
        assert 'categories' in status


def test_list_message_detailed_statuses(whispir, cassette):
    # message ID here is explicitly specified as it's easier than to
    # send a response back from test
    message = whispir.messages.Message(id='64271CF61AE5F786')
    statuses = message.statuses.list(view='detailed')
    statuses = list(statuses)
    assert len(statuses) > 0
    for status in statuses:
        assert isinstance(status, MessageStatus)
        assert 'status' in status


def test_list_message_responses(workspace, cassette):
    # message ID here is explicitly specified as it's easier than to
    # send a response back from test
    message = workspace.messages.Message(id='09CD9065116DF39F')
    responses = message.responses.list()
    responses = list(responses)
    assert len(responses) > 0
    for response in responses:
        assert isinstance(response, MessageResponse)
        assert 'responseCount' in response


def _check_message(message):
    assert isinstance(message, Message)
    assert 'id' in message
    assert 'subject' in message


def test_list_generic_messages(whispir, cassette):
    messages = whispir.messages.list()
    _check_list_messages(messages)


def test_list_messages(workspace, cassette):
    messages = workspace.messages.list()
    _check_list_messages(messages)


def _check_list_messages(messages):
    messages = list(itertools.islice(messages, 25))
    assert len(messages) > 0
    for message in messages:
        assert isinstance(message, Message)
        assert 'id' in message
        assert 'subject' in message


def _check_created_message(message, cassette):
    assert len(cassette) == 1
    location = cassette.responses[-1]['headers']['Location'][0]
    assert message['id'] == _msg_location(location)
    assert isinstance(message, Message)


def _msg_location(url):
    path = urlparse(url).path
    return path.split('/')[-1]
