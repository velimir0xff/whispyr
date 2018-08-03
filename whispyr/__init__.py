# -*- coding: utf-8 -*-

"""Top-level package for whispyr."""

__author__ = """Grigory Starinkin"""
__email__ = 'starinkin@gmail.com'
__version__ = '0.2.0'

from .whispyr import Whispir, WhispirRetry

from .whispyr import Message, MessageStatus, MessageResponse, Template, \
    Workspace, ResponseRule, Contact, App

from .whispyr import WhispirError, ClientError, ServerError, JSONDecodeError

__all__ = [
    # Client
    'Whispir', 'WhispirRetry',
    # Resources
    'Message', 'MessageStatus', 'MessageResponse', 'Template', 'Workspace',
    'ResponseRule', 'Contact', 'App',
    # Errors
    'WhispirError', 'ClientError', 'ServerError', 'JSONDecodeError'
]
