# -*- coding: utf-8 -*-

"""Templates tests for `whispyr` package"""

from whispyr.whispyr import Template
from collections import Iterable


def test_create_template(whispir, cassette):
    workspace = whispir.workspaces.Workspace(id='8080DE5434485ED4')
    template = workspace.templates.create(
        messageTemplateName='Whispyr test template',
        messageTemplateDescription='Create templates test',
        subject='test template',
        body='This is the body of my test SMS message',
        email={},
        voice={},
        web={})
    _check_template_instance(template)


def test_create_generic_template(whispir, cassette):
    template = whispir.templates.create(
        messageTemplateName='Whispyr test generic template',
        messageTemplateDescription='Create templates test',
        subject='test template',
        body='This is the body of my test SMS message',
        email={},
        voice={},
        web={})
    _check_template_instance(template)


def test_list_templates(whispir, cassette):
    workspace = whispir.workspaces.Workspace(id='8080DE5434485ED4')
    templates = workspace.templates.list()
    templates = list(templates)
    assert len(templates) > 0
    for template in templates:
        _check_template_instance(template)


def test_show_template(whispir, cassette):
    workspace = whispir.workspaces.Workspace(id='8080DE5434485ED4')
    template = workspace.templates.show('EBC0F5EBB8AA2B39')
    _check_template_instance(template)


def test_show_generic_template(whispir, cassette):
    template = whispir.templates.show('F0B35D18CA4984E7')
    _check_template_instance(template)


def test_update_template(whispir, cassette):
    workspace = whispir.workspaces.Workspace(id='8080DE5434485ED4')
    template = workspace.templates.show('EBC0F5EBB8AA2B39')
    description = template['messageTemplateDescription']
    new_description = '{} updated'.format(description)
    workspace.templates.update(
        template['id'],
        messageTemplateName=template['messageTemplateName'],
        messageTemplateDescription=new_description,
        subject=template['subject'],
        body=template['body'])
    updated_template = workspace.templates.show('EBC0F5EBB8AA2B39')
    _check_template_instance(updated_template)
    assert updated_template['messageTemplateDescription'] == new_description


def test_delete_template(whispir, cassette):
    workspace = whispir.workspaces.Workspace(id='8080DE5434485ED4')
    workspace.templates.delete('EBC0F5EBB8AA2B39')


def test_delete_generic_template(whispir, cassette):
    whispir.templates.delete('F0B35D18CA4984E7')


def _check_template_instance(template):
    assert isinstance(template, Template)
    assert 'id' in template
    assert 'messageTemplateName' in template
    assert 'messageTemplateDescription' in template
