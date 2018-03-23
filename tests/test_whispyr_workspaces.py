# -*- coding: utf-8 -*-


"""Tests for `whispyr` workspaces"""

from collections import Iterable, MutableMapping


def test_create_workspace(cassette, whispir):
    workspace = whispir.workspaces.create(
        projectName='whispyr tests', status='A')
    assert isinstance(workspace, MutableMapping)
    assert 'id' in workspace


def test_list_workspaces(cassette, whispir):
    workspaces = whispir.workspaces.list()
    assert isinstance(workspaces, Iterable)
    workspaces = list(workspaces)
    assert len(workspaces) > 0
    for workspace in workspaces:
        _check_workspace(workspace)


def test_show_workspace(cassette, whispir):
    workspace = whispir.workspaces.show('8080DE5434485ED4')
    _check_workspace(workspace)


def _check_workspace(workspace):
    assert isinstance(workspace, MutableMapping)
    assert 'id' in workspace
    assert 'projectName' in workspace
