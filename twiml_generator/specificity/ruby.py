from twiml_generator.specificity.common import Language


class Ruby(Language):

    _classes = {}

    @classmethod
    def clean(cls, generator):
        """Ruby library specificities which requires to change the TwiML IR."""

        for verb, event in generator.twimlir:
            cls.verb_processing(verb, generator.specific_imports)


@Ruby.register
class Play:

    @classmethod
    def process(cls, verb, imports):
        if verb.text:
            verb.attributes['url'] = verb.text
            verb.text = None


@Ruby.register
class Message:

    @classmethod
    def process(cls, verb, imports):
        if verb.text:
            verb.attributes['body'] = verb.text
            verb.text = None


@Ruby.register
class Dial:

    @classmethod
    def process(cls, verb, imports):
        if verb.text:
            verb.attributes['number'] = verb.text
            verb.text = None


@Ruby.register
class Say:

    @classmethod
    def process(cls, verb, imports):
        # the `message` is optional and should be passed as a keyword argument
        if verb.text:
            verb.attributes['message'] = verb.text
            verb.text = None


@Ruby.register
class Enqueue:

    @classmethod
    def process(cls, verb, imports):
        if verb.text:
            verb.attributes['name'] = verb.text
            verb.text = None


@Ruby.register
class Client:

    @classmethod
    def process(cls, verb, imports):
        if verb.text:
            verb.attributes['identity'] = verb.text
            verb.text = None
