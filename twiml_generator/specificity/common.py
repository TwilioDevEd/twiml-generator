from typing import Type


def rename_attr(verb, attr_name, new_name):
    """Rename attribute if found"""
    if attr_name in verb.attributes:
        verb.attributes[new_name] = verb.attributes.pop(attr_name)


def attr_to_list(verb, attr_name, formatter='{}', force=False,
                 transform=None):
    """Helper to convert string to language specific list or array

    :arg formatter: String to insert the values depending on language
    :arg force: Set to True to force conversion even when a single
     element is found
    :arg transform: function to modify each value before building the list
    :returns: True if converted to array
    """
    if attr_name in verb.attributes \
            and not isinstance(verb.attributes[attr_name], bytes):
        if ' ' in verb.attributes[attr_name] or force:
            verb.attributes[attr_name] = formatter.format(
                ', '.join([transform and transform(value) or value for value
                           in verb.attributes[attr_name].split(' ')])
            )
            return True
        verb.attributes[attr_name] = transform(verb.attributes[attr_name])
    return False


def to_bytes(verb, attr_name):
    """Convert string attribute to bytes

    * Works as mark to not wrap it as string on code generation
    """
    if attr_name in verb.attributes \
            and not isinstance(verb.attributes[attr_name], bytes):
        verb.attributes[attr_name] = verb.attributes[attr_name].encode('utf-8')


class Language:
    _classes = None

    @classmethod
    def register(cls, class_: Type) -> Type:
        cls._classes[getattr(class_, 'name', class_.__name__)] = class_
        return class_

    @classmethod
    def verb_processing(cls, verb, imports):
        """Process the verb with its respective class if exists"""

        if verb.name in cls._classes:
            cls._classes[verb.name].process(verb, imports)

    @classmethod
    def clean(cls, generator) -> None:
        raise NotImplementedError()

