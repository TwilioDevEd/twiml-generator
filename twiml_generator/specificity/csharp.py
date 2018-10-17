from functools import partial

from inflection import camelize, underscore

from twiml_generator.specificity import to_list as attr_to_list, to_bytes


def verb_processing(verb, generator):
    """Process the verb with its respective class if exists"""

    # Add any new verb class to this list to be processed
    verbs = [Prompt, Pay, Play]
    try:
        class_ = eval(verb.name)
    except NameError:
        pass
    else:
        if class_ in verbs:
            class_.process(verb, generator.specific_imports)


def to_list(verb, attr_name, imports, **kwargs):
    attr_to_list(verb, attr_name, formatter="new []{{{}}}.ToList()", **kwargs)
    if 'using System.Linq;' not in imports:
        imports.add('using System.Linq;')


def enum_name(verb_name, attr_name, value):
    return '.'.join([
        verb_name,
        camelize(attr_name + "Enum"),
        camelize(underscore(value))
    ])


def enum_builder(verb, attr_name):
    return partial(enum_name, verb.name, attr_name)


def to_enum(verb, attr_name):
    """Convert value to Enum"""
    if attr_name in verb.attributes and not isinstance(
            verb.attributes[attr_name], bytes):
        verb.attributes[attr_name] = enum_name(verb.name, attr_name,
                                               verb.attributes[attr_name])


def build_uri(value):
    return 'new Uri("{}")'.format(value)


def to_uri(verb, attr_name):
    """Translate the uri string to a new Uri object"""
    if attr_name in verb.attributes and not isinstance(
            verb.attributes[attr_name], bytes):
        verb.attributes[attr_name] = build_uri(verb.attributes[attr_name])


class Prompt:

    @classmethod
    def process(cls, verb, imports):
        to_list(verb, 'errorType', imports, force=True,
                transform=enum_builder(verb, 'errorType'))
        to_bytes(verb, 'errorType')

        to_list(verb, 'cardType', imports, force=True,
                transform=enum_builder(verb, 'cardType'))
        to_bytes(verb, 'cardType')

        to_list(verb, 'attempt', imports, force=True)
        to_bytes(verb, 'attempt')


class Pay:

    @classmethod
    def process(cls, verb, imports):
        to_list(verb, 'validCardTypes', imports, force=True,
                transform=enum_builder(verb, 'validCardTypes'))
        to_bytes(verb, 'validCardTypes')

        to_bytes(verb, 'timeout')

        to_bytes(verb, 'maxAttempts')


class Play:

    @classmethod
    def process(cls, verb, imports):
        if not verb.text:
            verb.text = ' '
        verb.text = build_uri(verb.text).encode('utf-8')
        imports.add("using System;")
