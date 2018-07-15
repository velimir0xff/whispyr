# -*- coding: utf-8 -*-

"""YAML serializer"""

import yaml

# Use the libYAML versions if possible
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


def deserialize(cassette_string):
    return yaml.load(cassette_string, Loader=Loader)


class PrettyDumper(Dumper):
    def increase_indent(self, flow=False, indentless=False):
        """this function indent collections to get this:

        foo:
          - bar
        quz:
          - baz

        instead of default:

        foo:
        - bar
        quz:
        - baz

        """
        return super(PrettyDumper, self).increase_indent(flow, False)


def literal_string_representer(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')


class literal_string(str):
    pass


def serialize(cassette_dict):
    for interaction in cassette_dict['interactions']:
        response = interaction['response']
        response_body = response['body']
        if response_body is not None:
            string = response_body.get('string', None)
            if string:
                response_body['string'] = literal_string(string)

        request = interaction['request']
        request_body = request['body']
        if request_body is not None:
            request['body'] = literal_string(request_body)
    yaml.add_representer(literal_string, literal_string_representer)
    return yaml.dump(
        cassette_dict, Dumper=PrettyDumper, default_flow_style=False)
