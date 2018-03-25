# -*- coding: utf-8 -*-

"""Templates tests for `whispyr` package"""

import pytest
import uuid

from whispyr import Template, ClientError


@pytest.fixture(params=[True])
def template(request, workspace):
    delete = request.param
    return _create_fixture_template(
        request, workspace.templates, delete=delete)


@pytest.fixture(params=[True])
def generic_template(request, whispir):
    delete = request.param
    return _create_fixture_template(
        request, whispir.templates, delete=delete)


@pytest.fixture(params=[2])
def templates(workspace, request):
    num = request.param
    templates = []
    for _ in range(num):
        name = str(uuid.uuid4())
        template = _create_fixture_template(request, workspace.templates, name)
        templates.append(template)
    return templates


def _create_fixture_template(request, templates,
                             name='Whispyr test template',
                             description='Create templates test',
                             delete=True):
    template = templates.create(
        messageTemplateName=name,
        messageTemplateDescription=description,
        subject='test template',
        body='This is the body of my test SMS message',
        email={},
        voice={},
        web={}
    )

    if delete:
        def _delete_template():
            templates.delete(template['id'])

        request.addfinalizer(_delete_template)

    return template


@pytest.mark.parametrize('templates', [4], indirect=True)
def test_list_templates(workspace, cassette, templates):
    templates = workspace.templates.list()
    templates = list(templates)
    assert len(templates) == 4
    for template in templates:
        _check_template_instance(template)


@pytest.mark.xfail(reason='TODO: Pagination seems to be broken on whispir side')
@pytest.mark.parametrize('templates', [55], indirect=True)
def test_list_templates_paginated(request, workspace, cassette, templates):
    templates = workspace.templates.list()
    templates = list(templates)
    assert len(templates) == 55
    for template in templates:
        _check_template_instance(template)


def test_show_template(workspace, cassette, template):
    _test_show_template(workspace.templates, template['id'])


def test_show_generic_template(whispir, cassette, generic_template):
    _test_show_template(whispir.templates, generic_template['id'])


def _test_show_template(templates, template_id):
    template = templates.show(template_id)
    _check_template_instance(template)


def test_update_template(workspace, cassette, template):
    description = template['messageTemplateDescription']
    new_description = '{} updated'.format(description)
    workspace.templates.update(
        template['id'],
        messageTemplateName=template['messageTemplateName'],
        messageTemplateDescription=new_description,
        subject=template['subject'],
        body=template['body'])
    updated_template = workspace.templates.show(template['id'])
    _check_template_instance(updated_template)
    assert updated_template['messageTemplateDescription'] == new_description


@pytest.mark.parametrize('template', [False], indirect=True)
def test_delete_template(workspace, cassette, template):
    _test_delete(workspace.templates, template)

@pytest.mark.parametrize('generic_template', [False], indirect=True)
def test_delete_generic_template(whispir, cassette, generic_template):
    _test_delete(whispir.templates, generic_template)


def _test_delete(templates, template):
    templates.delete(template['id'])
    with pytest.raises(ClientError) as excinfo:
        templates.show(template['id'])

    exc = excinfo.value
    assert exc.response.status_code == 404


def _check_template_instance(template):
    assert isinstance(template, Template)
    assert 'id' in template
    assert 'messageTemplateName' in template
    assert 'messageTemplateDescription' in template
