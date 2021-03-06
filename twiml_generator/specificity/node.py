from inflection import camelize

from twiml_generator.specificity.common import Language


class Node(Language):

    @classmethod
    def clean(cls, generator):
        for verb, event in generator.twimlir:
            if verb.name == 'break':
                verb.name = 'break_'
            if verb.is_ssml:
                verb.name = camelize(verb.name,
                                     uppercase_first_letter=False)
