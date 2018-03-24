# -*- coding: utf-8 -*-

"""Console script for whispyr."""

import click
import configparser
import json
import logging
import os
import sys

from pygments import highlight, lexers, formatters
from whispyr import Whispir

LOGGING_LEVELS = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR]


def setup_logging(verbosity):
    level = LOGGING_LEVELS[-(verbosity + 1)]

    if level <= logging.DEBUG:
        try:  # for Python 3
            from http.client import HTTPConnection
        except ImportError:
            from httplib import HTTPConnection
        HTTPConnection.debuglevel = 1

    # you need to initialize logging, otherwise you will not see
    # anything from requests
    logging.basicConfig()

    logging.getLogger().setLevel(level)
    requests_log = logging.getLogger("urllib3")
    requests_log.setLevel(level)
    requests_log.propagate = True


def config_paths(app_name='whispyr', file_name='config.ini'):
    for force_posix in [True, False]:
        app_dir = click.get_app_dir(app_name, force_posix=force_posix)
        yield os.path.join(app_dir, file_name)


class ClickSection:

    def __init__(self, section):
        self.section = section

    def get(self, key):
        section = self.section
        return section.get(key, fallback=None)


class ClickConfig:

    def __init__(self, config, section_name=None):
        self.config = config
        self._section = section_name or config.default_section

    def get(self, key):
        config = self.config
        section = config[key] if key in config else None
        if section:
            return ClickSection(section)
        return config.get(self._section, key, fallback=None)


def read_config():
    config = configparser.ConfigParser(default_section='default')
    paths = config_paths()
    config.read(paths)
    return ClickConfig(config)


CONTEXT_SETTINGS = dict(default_map=read_config())

@click.group(context_settings=CONTEXT_SETTINGS)
@click.option('-u', '--username', prompt=True)
@click.password_option('-p', '--password', confirmation_prompt=False)
@click.password_option('-a', '--api-key', confirmation_prompt=False)
@click.option('-w', '--workspace')
@click.option('-v', 'verbosity', count=True, default=0,
              type=click.IntRange(0, len(LOGGING_LEVELS) - 1, clamp=True))
@click.version_option()
@click.pass_context
def cli(ctx, username, password, api_key, workspace, verbosity):
    """Command line interface for Whispir API"""
    setup_logging(verbosity)
    ctx.obj = Whispir(username, password, api_key)


@cli.group()
@click.pass_context
def messages(ctx):
    """send and view all sorts of messages"""
    ctx.obj = ctx.obj.messages


@cli.group()
@click.pass_context
def workspaces(ctx):
    """create and view workspaces"""
    ctx.obj = ctx.obj.workspaces


@workspaces.command()
@click.pass_obj
def list(workspaces):
    """get list of workspaces"""
    echo_json(dict_list(workspaces.list()))


@messages.command()
@click.pass_obj
def list(messages):
    """get list of recent messages"""
    echo_json(dict_list(messages.list()))


@messages.group()
@click.pass_obj
def send(messages):
    """send messages"""


@send.command()
@click.argument('to')
@click.argument('subject')
@click.argument('body')
@click.pass_obj
def sms(messages, **kwargs):
    """send SMS"""
    resp = messages.create(**kwargs)
    echo_json(resp)


def echo_json(obj):
    formatted = json.dumps(obj, indent=2)
    colored = highlight(
        formatted, lexers.JsonLexer(), formatters.TerminalFormatter())
    click.echo(colored)


def dict_list(items):
    return [dict(it) for it in items]


def valid_json(ctx, param, value):
    try:
        return json.load(value)
    except json.JSONDecodeError as e:
        raise click.BadParameter('failed to parse JSON: {}'.format(e))


@send.command()
@click.argument('message', type=click.File('rb'), callback=valid_json)
@click.pass_obj
def raw(messages, message):
    """send JSON as a plain request to messages API"""
    messages.create(**message)


def main():
    sys.exit(cli(auto_envvar_prefix='WHISPYR'))

if __name__ == "__main__":
    main()  # pragma: no cover
