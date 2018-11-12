from twiml_generator.specificity.common import Language


class PHP(Language):
    _classes = {}

    @classmethod
    def clean(cls, generator):
        for verb, event in generator.twimlir:
            if verb.name == 'break':
                verb.name = 'break_'

            cls.verb_processing(verb, generator.specific_imports)


class DefaultText:

    @classmethod
    def process(cls, verb, imports):
        if not verb.text:
            verb.text = ' '


@PHP.register
class Message(DefaultText):
    @classmethod
    def process(cls, verb, imports):
        if not verb.text:
            verb.text = ' '


@PHP.register
class Dial(DefaultText):
    pass


@PHP.register
class Play(DefaultText):
    pass
