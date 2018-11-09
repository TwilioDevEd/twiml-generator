from inflection import camelize

from twiml_generator.specificity.common import Language, rename_attr, to_bytes


class Python(Language):
    _classes = {}

    @classmethod
    def clean(cls, generator) -> None:
        """Python library specificities which requires to change the TwiML IR.
        """
        for verb, event in generator.twimlir:
            if verb.is_ssml:
                verb.name = f'ssml_{verb.name}'
            rename_attr(verb, 'from', 'from_')
            rename_attr(verb, 'for', 'for_')

            cls.verb_processing(verb, generator.specific_imports)

    @classmethod
    def verb_processing(cls, verb, imports):
        super().verb_processing(verb, imports)

        for name, value in verb.attributes.items():
            if value in ['true', 'false']:
                verb.attributes[name] = camelize(value)
                to_bytes(verb, name)


@Python.register
class Play:

    @classmethod
    def process(cls, verb, imports):
        if not verb.text:
            verb.text = ' '
