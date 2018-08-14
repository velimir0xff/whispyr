# -*- coding: utf-8 -*-

"""Tests for `whispyr` workspaces"""

from whispyr import Workspace


def test_create_workspace(cassette, whispir, rand_name):
    workspace = whispir.workspaces.create(projectName=rand_name, status='A')
    assert isinstance(workspace, Workspace)
    assert 'id' in workspace


def test_list_workspaces(cassette, whispir):
    workspaces = whispir.workspaces.list()
    workspaces = list(workspaces)
    assert len(workspaces) > 0
    for workspace in workspaces:
        _check_workspace(workspace)


def test_show_workspace(whispir, workspace, cassette):
    workspace = whispir.workspaces.show(workspace['id'])
    _check_workspace(workspace)


def _check_workspace(workspace):
    assert isinstance(workspace, Workspace)
    assert 'id' in workspace
    assert 'projectName' in workspace
