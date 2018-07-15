# -*- coding: utf-8 -*-


"""Response rules tests for `whispyr` package"""

import pytest
import uuid

from whispyr import ResponseRule, ClientError


@pytest.mark.parametrize('response_rules', [4], indirect=True)
def test_list_response_rules(workspace, cassette, response_rules):
    _check_list(workspace, response_rules, 4)


@pytest.mark.parametrize('response_rules', [55], indirect=True)
def test_list_response_rules_paginated(workspace, cassette, response_rules):
    _check_list(workspace, response_rules, 55)


def test_show_response_rule(workspace, cassette, response_rule):
    response_rule = workspace.response_rules.show(response_rule['id'])
    _check_basic_response_rule(response_rule)


def test_show_generic_response_rule(whispir, cassette, generic_response_rule):
    response_rule = whispir.response_rules.show(generic_response_rule['id'])
    _check_basic_response_rule(response_rule)


def test_update_reponse_rule(workspace, cassette, response_rule):
    rule_id = response_rule['id']
    name = response_rule['name']
    description = response_rule['description']
    new_name = '{} updated'.format(name)
    new_description = '{} updated'.format(description)
    workspace.response_rules.update(
        rule_id,
        name=new_name,
        description=new_description,
        responseTemplatePatterns=response_rule['responseTemplatePatterns']
    )
    updated_rule = workspace.response_rules.show(rule_id)
    assert updated_rule['name'] == new_name
    assert updated_rule['description'] == new_description


@pytest.mark.parametrize('response_rule', [False], indirect=True)
def test_delete_response_rule(workspace, cassette, response_rule):
    _test_delete(workspace.response_rules, response_rule['id'])


@pytest.mark.parametrize('generic_response_rule', [False], indirect=True)
def test_delete_generic_response_rule(
        whispir, cassette, generic_response_rule):
    _test_delete(whispir.response_rules, generic_response_rule['id'])


def _test_delete(response_rules, rule_id):
    response_rules.delete(rule_id)
    with pytest.raises(ClientError) as excinfo:
        response_rules.show(rule_id)

    exc = excinfo.value
    assert exc.response.status_code == 404


@pytest.fixture(params=[True])
def response_rule(request, workspace):
    delete = request.param
    return _create_fixture_rule(
        request, workspace.response_rules, delete=delete)


@pytest.fixture(params=[True])
def generic_response_rule(request, whispir):
    delete = request.param
    return _create_fixture_rule(
        request, whispir.response_rules, delete=delete)


@pytest.fixture(params=[2])
def response_rules(request, workspace):
    num = request.param
    return [_create_fixture_rule(request, workspace.response_rules)
            for _ in range(num)]


def _create_fixture_rule(request, response_rules, delete=True):
    rule = {
        'name': str(uuid.uuid4()),
        'description': str(uuid.uuid4()),
        'responseTemplatePatterns': {
            'responseTemplatePattern': [{
                'name': str(uuid.uuid4()),
                'textPrompt': 'YES',
                'voicePrompt': '1',
                'spokenVoicePrompt': 'to select YES',
                'pattern': 'startswith',
                'colour': '#00947d'
            }]
        }
    }
    response_rule = response_rules.create(**rule)
    _check_basic_response_rule(response_rule)

    if delete:
        def _delete():
            response_rules.delete(response_rule['id'])

        request.addfinalizer(_delete)

    return response_rule


def _check_list(workspace, response_rules, expected_count):
    rules = workspace.response_rules.list()
    rules = list(rules)
    assert len(rules) == len(response_rules)
    assert len(rules) == expected_count
    for rule in rules:
        _check_basic_response_rule(rule)


def _check_basic_response_rule(response_rule):
    assert isinstance(response_rule, ResponseRule)
    assert 'id' in response_rule
    assert 'name' in response_rule
    assert 'description' in response_rule
