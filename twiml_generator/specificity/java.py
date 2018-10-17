from functools import partial

from inflection import underscore, camelize

from twiml_generator.specificity import to_list as attr_to_list, to_bytes, \
    rename_attr


def verb_processing(verb, generator):
    """Process the verb with its respective class if exists"""

    # Add any new verb class to this list to be processed
    verbs = [Prompt, Pay, Conference, Client, Number, Sip, Say, Reject, Dial,
             Enqueue, Play, SsmlBreak, SsmlEmphasis, SsmlPhoneme, SsmlSayAs]
    try:
        class_ = eval(verb.name)
    except NameError:
        pass
    else:
        if class_ in verbs:
            class_.process(verb, generator.specific_imports)


def to_list(verb, attr_name, imports, **kwargs):
    if attr_to_list(verb, attr_name, formatter="Arrays.asList({})", **kwargs)\
            and 'import java.util.Arrays;' not in imports:
        imports.add('import java.util.Arrays;')


def enum_name(verb_name, attr_name, value):
    return '.'.join([
        verb_name,
        camelize(attr_name),
        underscore(value).upper().replace('.', '_')
    ])


def enum_builder(verb, attr_name):
    return partial(enum_name, verb.name, attr_name)


def to_enum(verb, attr_name):
    if attr_name in verb.attributes and not isinstance(
            verb.attributes[attr_name], bytes):
        verb.attributes[attr_name] = enum_name(verb.name, attr_name,
                                               verb.attributes[attr_name])


class Say:

    @classmethod
    def process(cls, verb, imports):
        to_enum(verb, 'voice')
        to_bytes(verb, 'voice')

        to_enum(verb, 'language')
        to_bytes(verb, 'language')


class Reject:

    @classmethod
    def process(cls, verb, imports):
        to_enum(verb, 'reason')
        to_bytes(verb, 'reason')


class Dial:

    @classmethod
    def process(cls, verb, imports):
        to_enum(verb, 'record')
        to_bytes(verb, 'record')

        to_enum(verb, 'trim')
        to_bytes(verb, 'trim')


class Enqueue:

    @classmethod
    def process(cls, verb, imports):
        verb.attributes['queueName'] = verb.text
        verb.text = None


class Play:

    @classmethod
    def process(cls, verb, imports):
        if not verb.text:
            verb.text = ' '


class _Evented:

    @classmethod
    def event_name(cls, name):
        return cls.__name__ + '.Event.' + name.upper()

    @classmethod
    def process(cls, verb, imports):
        to_list(verb, 'statusCallbackEvent', imports,
                transform=cls.event_name)
        to_bytes(verb, 'statusCallbackEvent')
        rename_attr(verb, 'statusCallbackEvent', 'statusCallbackEvents')


class Client(_Evented):
    pass


class Number(_Evented):
    pass


class Sip(_Evented):
    pass


class Conference(_Evented):

    @classmethod
    def process(cls, verb, imports):
        super().process(verb, imports)
        to_enum(verb, 'beep')
        to_bytes(verb, 'beep')

        to_enum(verb, 'record')
        to_bytes(verb, 'record')


class Prompt:

    @classmethod
    def process(cls, verb, imports):
        to_enum(verb, 'for')
        to_bytes(verb, 'for')

        to_list(verb, 'cardType', imports,
                transform=enum_builder(verb, 'cardType'))
        to_bytes(verb, 'cardType')
        rename_attr(verb, 'cardType', 'cardTypes')

        to_list(verb, 'errorType', imports,
                transform=enum_builder(verb, 'errorType'))
        to_bytes(verb, 'errorType')
        rename_attr(verb, 'errorType', 'errorTypes')

        to_list(verb, "attempt", imports)
        to_bytes(verb, 'attempt')
        rename_attr(verb, 'attempt', 'attempts')


class Pay:

    @classmethod
    def process(cls, verb, imports):
        to_enum(verb, 'language')
        to_bytes(verb, 'language')

        to_list(verb, 'validCardTypes', imports,
                transform=enum_builder(verb, 'validCardTypes'))
        to_bytes(verb, 'validCardTypes')

        to_bytes(verb, 'maxAttempts')
        to_bytes(verb, 'timeout')


class SsmlBreak:

    @classmethod
    def process(cls, verb, imports):
        to_enum(verb, 'strength')
        to_bytes(verb, 'strength')


class SsmlPhoneme:

    @classmethod
    def process(cls, verb, imports):
        to_enum(verb, 'alphabet')
        to_bytes(verb, 'alphabet')


class SsmlSayAs:

    @classmethod
    def process(cls, verb, imports):
        rename_attr(verb, 'interpret-as', 'interpretAs')
        to_enum(verb, 'interpretAs')
        to_bytes(verb, 'interpretAs')

        to_enum(verb, 'role')
        to_bytes(verb, 'role')


class SsmlEmphasis:

    @classmethod
    def process(cls, verb, imports):
        to_enum(verb, 'level')
        to_bytes(verb, 'level')
