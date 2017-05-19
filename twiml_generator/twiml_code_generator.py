#!/usr/bin/env python
# coding: utf-8
import json
import logging
import subprocess

from pathlib import Path
from lxml import etree
from inflection import underscore, camelize

from .twimlir import TwimlIR

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def load_language_spec(language):
    """Load language specifications."""
    spec_filepath = Path(__file__).parent / 'languages_specs' / (language + '.json')
    logger.debug('Loading language spec file : {}'.format(spec_filepath))
    with spec_filepath.open() as f:
        spec = json.load(f)
    return spec


class TwimlCodeGenerator(object):
    """Class to generate the necessary code for outputing a given TwiML."""

    def __init__(self, twiml_filepath, code_filepath=None, language='python'):
        self.language_spec = load_language_spec(language)
        self.twiml_filepath = twiml_filepath
        self.twimlir = TwimlIR(twiml_filepath)
        if not code_filepath:
            self.code_filepath = self.get_code_filepath()
        elif not isinstance(code_filepath, Path):
            self.code_filepath = Path(code_filepath)
        else:
            self.code_filepath = code_filepath

        if language == 'java':
            self.clean_java_specificities()

    def get_code_filepath(self):
        """Return a path for the generator file to be written."""
        filepath = Path(self.twiml_filepath).resolve()
        generators_dirpath = filepath.parent.parent / 'generators'
        generators_dirpath.mkdir(exist_ok=True)
        language_dirpath = generators_dirpath / self.language_spec['language']
        language_dirpath.mkdir(exist_ok=True)
        code_filepath = language_dirpath / filepath.name.replace('.xml', self.language_spec['extension'])
        return code_filepath

    def __repr__(self):
        """Return the code to generate the TwiML."""
        if self.language_spec.get('reverse_build'):
            return self.__reverse_repr__()

        lines = []
        for verb, event in self.twimlir:
            if event == 'start':
                lines.append(self.output_new_variable(verb))
            elif event == 'leaf':
                lines.append(self.output_new_leaf(verb))
            elif event == 'end' and verb.parent:
                append_line = self.output_append(verb)
                if append_line != '':
                    lines.append(append_line)
        return self.output_wrapper(lines)

    def __reverse_repr__(self):
        lines = []
        for verb in self.twimlir.reverse_iter():
            if verb.is_leaf:
                lines.append(self.output_new_leaf(verb))
            else:
                lines.append(self.output_new_variable(verb))
        return self.output_wrapper(lines)

    def output_imports(self):
        """Return a string containing the imports lines for the code."""
        if self.twimlir.is_voice_response:
            import_kind = 'import_voice'
        else:
            import_kind = 'import_messaging'

        imports = self.twimlir.verb_names
        if self.language_spec.get('necessary_imports'):
            imports.extend(self.language_spec['necessary_imports'])

        if self.language_spec.get('add_imports') == 'single_line':
            imports = [verb if verb != 'Response' else self.class_for_verb_name(verb) for verb in imports]
            return self.language_spec[import_kind].format(
                imports=', '.join(imports)
            ) + '\n'
        elif self.language_spec.get('add_imports') == 'multiple_lines':
            imports = [verb if verb != 'Response' else self.class_for_verb_name(verb) for verb in imports]
            return '\n'.join([self.language_spec[import_kind].format(imports=i) for i in imports]) + '\n'
        else:
            return self.language_spec[import_kind] + '\n'

    def output_new_variable(self, verb, appends=None):
        """Return a string to create a new tag that will contain other verbs."""
        if verb.parent and self.language_spec.get('new_block'):
            return self.language_spec['new_block'].format(
                variable=self.variable_for_verb(verb),
                parent=self.variable_for_verb(verb.parent),
                attributes=self.join_attributes_for_verb(verb),
                klass=self.class_for_verb(verb),
                text=self.quote_text_for_verb(verb),
                appends=self.join_appends(verb)
            )
        else:
            return self.language_spec['new_variable'].format(
                variable=self.variable_for_verb(verb),
                klass=self.class_for_verb(verb),
                attributes=self.join_attributes_for_verb(verb),
                text=self.quote_text_for_verb(verb),
                appends=self.join_appends(verb)
            )

    def output_new_leaf(self, verb):
        """Return a string for adding a simple verb to a parent."""
        if self.language_spec['language'] == 'java' and verb.name in ['Body', 'Media']:
            return self.language_spec['new_leaf_no_builder'].format(
                parent=self.variable_for_verb(verb.parent),
                method=self.method_for_verb(verb),
                text=self.quote_text_for_verb(verb),
                attributes=self.join_attributes_for_verb(verb),
                klass=self.class_for_verb(verb),
                variable=self.variable_for_verb(verb)
            )
        else:
            return self.language_spec['new_leaf'].format(
                parent=self.variable_for_verb(verb.parent),
                method=self.method_for_verb(verb),
                text=self.quote_text_for_verb(verb),
                attributes=self.join_attributes_for_verb(verb),
                klass=self.class_for_verb(verb),
                variable=self.variable_for_verb(verb)
            )

    def output_append(self, verb):
        """Return a string to append a verb to its parent."""
        return self.language_spec['append'].format(
            parent=self.variable_for_verb(verb.parent),
            klass=self.class_for_verb(verb),
            variable=self.variable_for_verb(verb)
        )

    def output_print(self):
        """Return a string to print the TwiML result in the code."""
        return self.language_spec['print']

    def output_wrapper(self, lines):
        """Used to wrap code, structure imports and print out function in a single file."""
        if self.language_spec.get('code_wrapper'):
            return self.language_spec['code_wrapper'].format(
                imports=self.output_imports(),
                classname=camelize(str(self.code_filepath.name)[:-len(self.language_spec['extension'])]),
                code=self.output_padded_code(lines),
                print=self.output_padded_code(self.output_print().split('\n'))
            )
        else:
            return code

    def output_padded_code(self, lines):
        """Return a string containing all the lines left padded accordingly."""
        return '\n'.join([' ' * self.language_spec['code_wrapper_padding'] + line for line in lines]) + '\n'

    def variable_for_verb(self, verb):
        """Return a formated variable name for a given verb."""
        if not verb:
            return ''
        elif self.language_spec.get('variable_name_style') == 'camelize':
            return camelize(verb.name)
        else:
            return verb.name.lower()

    def method_for_verb(self, verb):
        """Return a formated method name for a given verb."""
        if self.language_spec.get('method_name_style') == 'camelize':
            return camelize(verb.name)
        else:
            return verb.name.lower()

    def class_for_verb(self, verb):
        """Return a formated class name for a given verb."""
        return self.class_for_verb_name(verb.name)

    def class_for_verb_name(self, verb_name):
        """Return a formated class name for a given verb name."""
        if verb_name == 'Response':
            if self.twimlir.is_voice_response:
                return self.language_spec['voice_class']
            else:
                return self.language_spec['messaging_class']
        else:
            return verb_name

    def quote_text_for_verb(self, verb):
        """Return the text quoted for the language."""
        if not verb.text:
            return ''
        quote = self.language_spec.get('string_quote', "'")
        text = self.language_spec['text_format'].format(
            text=quote + verb.text.replace(quote, '\\' + quote) + quote
        )
        if len(verb.attributes) == 0:
            if text.startswith(', '):
                text = text[2:]
            elif text.endswith(', '):
                text = text[:-2]
        return text

    def join_attributes_for_verb(self, verb):
        """Return a string containing the attributes to be used when calling the verb method."""
        if len(verb.attributes) > 0:
            attributes = self.build_attributes_for_verb(verb)
            joined_attributes = self.language_spec.get('attribute_join', ', ').join(attributes)
            return self.language_spec.get('attributes_wrapper_format', '{attributes}') \
                                     .format(attributes=joined_attributes)
        else:
            return ''

    def build_attributes_for_verb(self, verb):
        """Return a list of attributes declaration formated for the language to be joined."""
        built_attributes = []
        for name, value in verb.attributes.items():
            if self.language_spec.get('attribute_name_style') == 'underscore':
                name = underscore(name)
            if self.language_spec.get('attributes_map') \
               and self.language_spec['attributes_map'].get(name) \
               and self.language_spec['attributes_map'][name].get(value):
                value = self.language_spec['attributes_map'][name][value]
            elif isinstance(value, str) and self.language_spec.get('string_quote'):
                quote = self.language_spec['string_quote']
                value = quote + value + quote
            else:
                value = repr(value)
            built_attributes.append(self.language_spec['attribute_format'].format(name=name, value=value))
        return built_attributes

    def join_appends(self, verb):
        """Return a string with all the leaves to be appened to the current verb."""
        if self.language_spec.get('chained_append'):
            return ''.join(
                [self.language_spec['chained_append'].format(
                    variable=self.variable_for_verb(v))
                    for v in verb.children])
        else:
            return ''

    def clean_java_specificities(self):
        """Java library specificities which requires to change the TwiML IR."""
        for verb, event in self.twimlir:
            if verb.name == 'Redirect':
                verb.attributes['url'] = verb.text
                verb.text = None

    def write_code(self):
        """Write the code in the generator file."""
        if self.code_filepath.exists():
            self.code_filepath.unlink()
        self.code_filepath.write_text(str(self), encoding='utf-8')

    def verify(self):
        """Try to run the code and verify its output against the original TwiML."""
        parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, strip_cdata=True)
        logger.debug('Running: {} {}'.format(self.language_spec['language'], str(self.code_filepath)))
        p = subprocess.run([self.language_spec['language'], str(self.code_filepath)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if p.returncode == 0:
            old_tree = etree.parse(self.twiml_filepath, parser)
            new_tree = etree.fromstring(p.stdout, parser)
            print('OLD:\n' + etree.tostring(old_tree, encoding='utf-8', pretty_print=True).decode())
            print('NEW:\n' + etree.tostring(new_tree, encoding='utf-8', pretty_print=True).decode())
            print('### OLD == NEW ? {} ###'.format(self.etree_element_eq(old_tree.getroot(), new_tree)))
        else:
            print(p.stderr.decode())

    def etree_element_eq(self, a, b):
        """Return True if two etree (a and b) are equal."""
        return (a.tag == b.tag
                and a.tail == b.tail
                and a.attrib == b.attrib
                and (a.text.strip() == b.text.strip() if a.text and b.text else a.text == b.text)
                and len(a) == len(b)
                and all(self.etree_element_eq(c1, c2) for c1, c2 in zip(a, b)))
