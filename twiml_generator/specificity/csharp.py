from functools import partial

from inflection import camelize, underscore

from twiml_generator.specificity.common import attr_to_list, to_bytes, \
    Language, rename_attr


def to_list(verb, attr_name, imports, **kwargs):
    attr_to_list(verb, attr_name, formatter="new []{{{}}}.ToList()", **kwargs)
    if attr_name in verb.attributes:
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
    optional_kind = ''
    if (
        not value.startswith('/')
        and not value.startswith('http')
        and not value.startswith('sip:')
    ):
        optional_kind = ', UriKind.Relative'
    return f'new Uri("{value}"{optional_kind})'


def text_to_uri(verb):
    if verb.text:
        verb.text = build_uri(verb.text).encode('utf-8')
        if verb.attributes:
            verb.text += b', '


def to_uri(verb, attr_name):
    """Translate the uri string to a new Uri object"""
    if attr_name in verb.attributes and not isinstance(
            verb.attributes[attr_name], bytes):
        verb.attributes[attr_name] = build_uri(verb.attributes[attr_name])


class CSharp(Language):
    _classes = {}

    @classmethod
    def clean(cls, generator) -> None:
        """C# library specificities which requires to change the TwiML IR."""
        for verb, event in generator.twimlir:
            rename_attr(verb, 'for', 'for_')

            if verb.is_ssml:
                verb.name = camelize(verb.name)

            cls.verb_processing(verb, generator.specific_imports)


@CSharp.register
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


@CSharp.register
class Pay:

    @classmethod
    def process(cls, verb, imports):
        to_list(verb, 'validCardTypes', imports, force=True,
                transform=enum_builder(verb, 'validCardTypes'))
        to_bytes(verb, 'validCardTypes')

        to_bytes(verb, 'timeout')

        to_bytes(verb, 'maxAttempts')

        to_uri(verb, 'action')
        to_bytes(verb, 'action')


@CSharp.register
class Play:

    @classmethod
    def process(cls, verb, imports):
        text_to_uri(verb)


@CSharp.register
class SayAs:
    name = "say-as"

    @classmethod
    def process(cls, verb, imports):
        rename_attr(verb, 'interpret-as', 'interpretAs')


@CSharp.register
class Redirect:

    @classmethod
    def process(cls, verb, imports):
        verb.attributes['url'] = verb.text
        verb.text = None
        to_uri(verb, 'url')
        to_bytes(verb, 'url')


@CSharp.register
class Gather:

    @classmethod
    def process(cls, verb, imports):
        to_uri(verb, 'action')
        to_bytes(verb, 'action')
        to_list(verb, 'input', imports, force=True,
                transform=enum_builder(verb, 'Input'))
        to_bytes(verb, 'input')


@CSharp.register
class Media:

    @classmethod
    def process(cls, verb, imports):
        text_to_uri(verb)


@CSharp.register
class Message:

    @classmethod
    def process(cls, verb, imports):
        to_uri(verb, 'action')
        to_bytes(verb, 'action')


@CSharp.register
class Record:

    @classmethod
    def process(cls, verb, imports):
        to_uri(verb, 'action')
        to_bytes(verb, 'action')
        to_uri(verb, 'transcribeCallback')
        to_bytes(verb, 'transcribeCallback')


class Evented:

    @classmethod
    def process(cls, verb, imports):
        to_uri(verb, 'statusCallback')
        to_bytes(verb, 'statusCallback')

        to_list(verb, 'statusCallbackEvent', imports, force=True,
                transform=enum_builder(verb, 'Event'))
        to_bytes(verb, 'statusCallbackEvent')


@CSharp.register
class Number(Evented):

    @classmethod
    def process(cls, verb, imports):
        super().process(verb, imports)

        to_uri(verb, 'url')
        to_bytes(verb, 'url')


@CSharp.register
class Client(Evented):
    pass


@CSharp.register
class Conference(Evented):

    @classmethod
    def process(cls, verb, imports):
        super().process(verb, imports)

        to_enum(verb, 'beep')
        to_bytes(verb, 'beep')

        to_uri(verb, 'waitUrl')
        to_bytes(verb, 'waitUrl')

        to_enum(verb, 'record')
        to_bytes(verb, 'record')

        to_enum(verb, 'region')
        to_bytes(verb, 'region')

        to_enum(verb, 'trim')
        to_bytes(verb, 'trim')

        to_uri(verb, 'recordingStatusCallback')
        to_bytes(verb, 'recordingStatusCallback')

        to_uri(verb, 'eventCallbackUrl')
        to_bytes(verb, 'eventCallbackUrl')

        to_list(verb, 'recordingStatusCallbackEvent', imports, force=True,
                transform=enum_builder(verb, 'Event'))
        to_bytes(verb, 'recordingStatusCallbackEvent')


@CSharp.register
class Dial:

    @classmethod
    def process(cls, verb, imports):
        to_uri(verb, 'action')
        to_bytes(verb, 'action')

        to_enum(verb, 'record')
        to_bytes(verb, 'record')

        to_enum(verb, 'trim')
        to_bytes(verb, 'trim')

        to_uri(verb, 'recordingStatusCallback')
        to_bytes(verb, 'recordingStatusCallback')

        to_uri(verb, 'referUrl')
        to_bytes(verb, 'referUrl')

        to_list(verb, 'recordingStatusCallbackEvent', imports, force=True,
                transform=enum_builder(verb, 'Event'))
        to_bytes(verb, 'recordingStatusCallbackEvent')

        to_enum(verb, 'ringTone')
        to_bytes(verb, 'ringTone')


@CSharp.register
class Connect:

    @classmethod
    def process(cls, verb, imports):
        to_uri(verb, 'action')
        to_bytes(verb, 'action')

        if 'timeout' in verb.attributes:
            verb.attributes.pop('timeout')


@CSharp.register
class Room(Evented):
    pass


@CSharp.register
class Enqueue:

    @classmethod
    def process(cls, verb, imports):
        to_uri(verb, 'action')
        to_bytes(verb, 'action')

        to_uri(verb, 'waitUrl')
        to_bytes(verb, 'waitUrl')


@CSharp.register
class Queue:

    @classmethod
    def process(cls, verb, imports):
        to_uri(verb, 'url')
        to_bytes(verb, 'url')

@CSharp.register
class Refer:

    @classmethod
    def process(cls, verb, imports):
        to_uri(verb, 'action')
        to_bytes(verb, 'action')

@CSharp.register
class Sip(Evented):

    @classmethod
    def process(cls, verb, imports):
        super().process(verb, imports)

        text_to_uri(verb)

        to_uri(verb, 'url')
        to_bytes(verb, 'url')


@CSharp.register
class Sms(Evented):

    @classmethod
    def process(cls, verb, imports):
        super().process(verb, imports)

        to_uri(verb, 'action')
        to_bytes(verb, 'action')
