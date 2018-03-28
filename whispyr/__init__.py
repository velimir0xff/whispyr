# -*- coding: utf-8 -*-

"""Top-level package for whispyr."""

__author__ = """Grigory Starinkin"""
__email__ = 'starinkin@gmail.com'
__version__ = '0.1.0'

from .whispyr import Whispir, Message, MessageStatus, MessageResponse, \
    Template, Workspace, ResponseRule

from .whispyr import WhispirError, ClientError, ServerError, JSONDecodeError
