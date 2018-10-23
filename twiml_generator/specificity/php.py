from twiml_generator.specificity.common import Language


class PHP(Language):

    @classmethod
    def clean(cls, generator):
        for verb, event in generator.twimlir:
            if verb.name == 'break':
                verb.name = 'break_'
