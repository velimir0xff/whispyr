# -*- coding: utf-8 -*-

"""Console script for whispyr."""

import sys
import click
import json
import pprint
import logging

import whispyr
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


@click.group()
@click.option('-u', '--username', prompt=True)
@click.password_option('-p', '--password', confirmation_prompt=False)
@click.password_option('-a', '--api-key', confirmation_prompt=False)
@click.option('-w', '--workspace', prompt=True)
@click.version_option()
@click.option('-v', 'verbosity', count=True, default=0,
              type=click.IntRange(0, len(LOGGING_LEVELS) - 1, clamp=True))
@click.pass_context
def cli(ctx, username, password, api_key, workspace, verbosity):
    """Command line interface for Whispir API"""
    setup_logging(verbosity)
    ctx.obj = Whispir(username, password, api_key, workspace=workspace)


@cli.group()
@click.pass_context
def messages(ctx):
    """send all sorts of messages"""
    ctx.obj = ctx.obj.messages

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
    click.echo(pprint.pformat(resp))


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
