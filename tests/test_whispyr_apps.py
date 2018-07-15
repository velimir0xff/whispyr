# -*- coding: utf-8 -*-


"""Apps tests for `whispyr` package"""

import pytest

from whispyr import App, ClientError


@pytest.mark.parametrize('apps', [4], indirect=True)
def test_list_apps(whispir, cassette, apps):
    _check_list(whispir, apps, 4)


@pytest.mark.parametrize('apps', [55], indirect=True)
def test_list_apps_paginated(whispir, cassette, apps):
    _check_list(whispir, apps, 55)


def test_show_app(whispir, cassette, app):
    app = whispir.apps.show(app['id'])
    _check_basic_app(app)


def test_update_app(whispir, cassette, app):
    app_id = app['id']
    name = app['name']
    description = app['description']
    new_name = '{} updated'.format(name)
    new_description = '{} updated'.format(description)
    whispir.apps.update(
        app_id,
        name=new_name,
        description=new_description,
        bundleId=app['bundleId']
    )
    updated_app = whispir.apps.show(app_id)
    assert updated_app['name'] == new_name
    assert updated_app['description'] == new_description


@pytest.mark.parametrize('app', [False], indirect=True)
def test_delete_app(whispir, cassette, app):
    _test_delete(whispir.apps, app['id'])


def _test_delete(apps, app_id):
    apps.delete(app_id)
    with pytest.raises(ClientError) as excinfo:
        apps.show(app_id)

    exc = excinfo.value
    assert exc.response.status_code == 404


def _check_list(workspace, apps, expected_count):
    apps = workspace.apps.list()
    apps = list(apps)
    assert len(apps) == len(apps)
    assert len(apps) == expected_count
    for app in apps:
        _check_basic_app(app)


def _check_basic_app(app):
    assert isinstance(app, App)
    assert 'id' in app
    assert 'name' in app
    assert 'description' in app
