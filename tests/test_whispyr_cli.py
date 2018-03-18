# -*- coding: utf-8 -*-

"""Tests for `whispyr` CLI interface."""

import pytest

from click.testing import CliRunner

import whispyr
from whispyr import cli


@pytest.fixture
def runner():
    return CliRunner()


def test_no_arguments(runner):
    """Test the CLI."""
    result = runner.invoke(cli.cli)
    assert result.exit_code == 0
    assert 'Command line interface for Whispir API' in result.output


def test_help_message(runner):
    help_result = runner.invoke(cli.cli, ['--help'])
    assert help_result.exit_code == 0
    assert 'Command line interface for Whispir API' in help_result.output
    assert 'Options:' in help_result.output
    assert '--version' in help_result.output


def test_no_args_the_same_as_help(runner):
    result = runner.invoke(cli.cli)
    help_result = runner.invoke(cli.cli, ['--help'])
    assert result.output == help_result.output


def test_show_version(runner):
    result = runner.invoke(cli.cli, ['--version'])
    assert result.exit_code == 0
    assert 'version {}'.format(whispyr.__version__) in result.output
