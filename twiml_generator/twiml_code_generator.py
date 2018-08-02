#!/usr/bin/env python
# coding: utf-8
import json
import logging
import os
import shutil
import subprocess

from pathlib import Path
from lxml import etree
from inflection import underscore
from inflection import camelize as pascalize

from .twimlir import TwimlIR

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def camelize(string):
    return pascalize(string, uppercase_first_letter=False)


def load_language_spec(language):
    """Load language specifications."""
    spec_filepath = Path(__file__).parent / 'languages_specs' / (language + '.json')
    logger.debug('Loading language spec file : {}'.format(spec_filepath))
    with spec_filepath.open() as f:
        spec = json.load(f)
    return spec


class TwimlCodeGenerator(object):
    """Class to generate the necessary code for outputing a given TwiML."""

    def __init__(self, twiml_filepath, code_filepath=None, lib_filepath=None, language='python'):
        self.language_spec = load_language_spec(language)
        self.twiml_filepath = Path(twiml_filepath)
        self.twimlir = TwimlIR(twiml_filepath)
        if not code_filepath:
            self.code_filepath = self.get_code_filepath()
        elif not isinstance(code_filepath, Path):
            self.code_filepath = Path(code_filepath)
        else:
            self.code_filepath = code_filepath

        if lib_filepath:
            self.lib_filepath = Path(lib_filepath)
        else:
            self.lib_filepath = Path(__file__).parent / '../lib'
        self.lib_filepath = self.lib_filepath.resolve()

        self.specific_imports = set()
        if language == 'java':
            self.clean_java_specificities()
        elif language == 'python':
            self.clean_python_specificities()
        elif language == 'csharp':
            self.clean_csharp_specificities()
        elif language == 'ruby':
            self.clean_ruby_specificities()
        elif language == 'node':
            self.clean_node_specifities()

    def overwrite_language_spec(self, key, value):
        self.language_spec[key] = value

    def get_code_filepath(self):
        """Return a path for the generator file to be written."""
        filepath = self.twiml_filepath.resolve()
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
            # Method for adding text after a closing tag
            # for example, append() in Python or addText() in node
            if verb.tail and not verb.tail.startswith('\n'):
                lines.append(self.output_new_text(verb))
            if self.language_spec.get('optional_parentheses', False):
                lines[-1] = lines[-1].replace('()', '')
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

        # Remove import statements for SSML_VERBS, since they are generally methods in the Say class
        imports = self.twimlir.get_verb_names(exclude_ssml_verbs=True)

        if self.language_spec.get('necessary_imports'):
            imports.extend(self.language_spec['necessary_imports'])

        if self.language_spec.get('add_imports') == 'single_line':
            imports = [verb if verb != 'Response' else self.class_for_verb_name(verb) for verb in imports]
            return self.language_spec[import_kind].format(
                imports=', '.join(imports)
            ) + '\n'
        elif self.language_spec.get('add_imports') == 'multiple_lines':
            classes_to_import = [verb if verb != 'Response' else self.class_for_verb_name(verb) for verb in imports]
            imports = []
            for class_name in classes_to_import:
                if self.language_spec.get('import_common') \
                   and class_name in self.language_spec.get('common_classes', []):
                    imports.append(self.language_spec['import_common'].format(imports=class_name))
                else:
                    imports.append(self.language_spec[import_kind].format(imports=class_name))
            imports = '\n'.join(imports) + '\n'
            if len(self.specific_imports) > 0:
                imports += '\n'.join(self.specific_imports)
            return imports
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
                appends=self.join_appends(verb),
                indent=self.indent_for_verb(verb)
            )
        else:
            return self.language_spec['new_variable'].format(
                variable=self.variable_for_verb(verb),
                klass=self.class_for_verb(verb),
                attributes=self.join_attributes_for_verb(verb),
                text=self.quote_text_for_verb(verb),
                appends=self.join_appends(verb),
                indent=self.indent_for_verb(verb)
            )

    def output_new_leaf(self, verb):
        """Return a string for adding a simple verb to a parent."""
        return self.language_spec['new_leaf'].format(
            parent=self.variable_for_verb(verb.parent),
            method=self.method_for_verb(verb),
            text=self.quote_text_for_verb(verb),
            attributes=self.join_attributes_for_verb(verb),
            klass=self.class_for_verb(verb),
            variable=self.variable_for_verb(verb),
            indent=self.indent_for_verb(verb)
        )

    def output_new_text(self, verb):
        """"""
        return self.language_spec['new_text'].format(
            parent=self.variable_for_verb(verb.parent),
            text=verb.tail.rstrip(),
            indent=self.indent_for_verb(verb)
        )

    def output_append(self, verb):
        """Return a string to append a verb to its parent."""
        return self.language_spec['append'].format(
            parent=self.variable_for_verb(verb.parent),
            klass=self.class_for_verb(verb),
            variable=self.variable_for_verb(verb),
            indent=self.indent_for_verb(verb)
        )

    def output_print(self):
        """Return a string to print the TwiML result in the code."""
        return self.language_spec['print']

    def output_wrapper(self, lines):
        """Used to wrap code, structure imports and print out function in a single file."""
        return self.language_spec['code_wrapper'].format(
            imports=self.output_imports(),
            classname=pascalize(underscore(str(self.twiml_filepath.name)[:-4])),
            code=self.output_padded_code(lines),
            print=self.output_padded_code(self.output_print().split('\n'))
        )

    def output_padded_code(self, lines):
        """Return a string containing all the lines left padded accordingly."""
        return '\n'.join([' ' * self.language_spec['code_wrapper_padding'] + line for line in lines]) + '\n'

    def variable_for_verb(self, verb):
        """Return a formated variable name for a given verb."""
        if not verb:
            return ''
        elif not verb.variable_name:
            if self.language_spec.get('variable_name_style') == 'camelize':
                variable_name = camelize(verb.name)
            elif self.language_spec.get('variable_name_style') == 'pascalize':
                variable_name = pascalize(verb.name)
            else:
                variable_name = verb.name.lower()
            number = 1
            verb.variable_name = variable_name
            while verb.variable_name in self.twimlir.generated_variables_names:
                number += 1
                verb.variable_name = variable_name + str(number)
            self.twimlir.generated_variables_names.add(verb.variable_name)
        return verb.variable_name

    def method_for_verb(self, verb):
        """Return a formated method name for a given verb."""
        if self.language_spec.get('method_name_style') == 'camelize':
            method_name = camelize(verb.name)
        elif self.language_spec.get('method_name_style') == 'pascalize':
            method_name = pascalize(verb.name)
        else:
            method_name = verb.name.lower()

        return method_name

    def class_for_verb(self, verb):
        """Return a formated class name for a given verb."""
        return self.class_for_verb_name(verb.name)

    def class_for_verb_name(self, verb_name):
        """Return a formated class name for a given verb name."""
        verb_name = pascalize(verb_name)
        if verb_name == 'Response':
            if self.twimlir.is_voice_response:
                return self.language_spec['voice_class']
            else:
                return self.language_spec['messaging_class']
        elif 'new_klass' in self.language_spec:
            return self.language_spec['new_klass'].format(klass=verb_name)
        else:
            return verb_name

    def quote_text_for_verb(self, verb):
        """Return the text quoted for the language."""
        if not verb.text:
            return ''
        if verb.text == ' ':
            verb.text = ''
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
            elif self.language_spec.get('attribute_name_style') == 'camelize':
                name = camelize(underscore(name))
            if self.language_spec.get('attributes_map') \
               and self.language_spec['attributes_map'].get(name) \
               and self.language_spec['attributes_map'][name].get(value):
                value = self.language_spec['attributes_map'][name][value]
                if self.language_spec['attributes_map'][name].get('_import'):
                    self.specific_imports.add(self.language_spec['attributes_map'][name]['_import'])
            elif self.language_spec.get('use_boolean') and value in ['true', 'false']:
                value = value
            elif isinstance(value, str) and self.language_spec.get('string_quote'):
                quote = self.language_spec['string_quote']
                value = quote + value + quote
            elif isinstance(value, bytes):
                value = value.decode('utf-8')
            else:
                value = repr(value)
            built_attributes.append(self.language_spec['attribute_format'].format(name=name, value=value))
        return built_attributes

    def indent_for_verb(self, verb):
        return '    ' * (verb.depth + self.language_spec.get('depth_padding', 0))

    def join_appends(self, verb):
        """Return a string with all the leaves to be appened to the current verb."""
        if self.language_spec.get('chained_append'):
            chain = []
            for v in verb.children:
                chain.append(self.language_spec['chained_append'].format(
                    method=self.method_for_verb(v),
                    variable=self.variable_for_verb(v)
                ))
                # Chained addText() method
                if v.tail and not v.tail.startswith('\n'):
                    if self.language_spec['language'] == 'java':
                        # In Java every method is chained, so we need to drop the parent
                        # E.g. ssmlP(p).addText("aaaaaa").ssmlPhoneme(phoneme).addText("bbbbbbb")
                        v.parent = ''
                    chain.append(self.output_new_text(v))
            return ''.join(chain)
        else:
            return ''

    def clean_java_specificities(self):
        """Java library specificities which requires to change the TwiML IR."""
        for verb, event in self.twimlir:
            if verb.is_ssml:
                verb.variable_name = camelize('ssml_' + verb.name)
                verb.name = pascalize('ssml_' + verb.name)
                import_name = f"import com.twilio.twiml.voice.{verb.name};"
                self.specific_imports.add(import_name)
            if verb.name == 'Enqueue':
                verb.attributes['queueName'] = verb.text
                verb.text = None
            elif verb.name == 'Play':
                if not verb.text:
                    verb.text = ' '
            elif verb.name == 'Dial':
                self.java_enumize(verb, 'record')
                self.java_enumize(verb, 'trim')
            elif verb.name == 'Reject':
                self.java_enumize(verb, 'reason')
            elif verb.name == 'Say':
                self.java_enumize(verb, 'voice')
                self.java_enumize(verb, 'language')
            elif verb.name in ['Client', 'Number', 'Sip']:
                if 'statusCallbackEvent' in verb.attributes:
                    verb.attributes['statusCallbackEvents'] = 'Arrays.asList({})'.format(
                        ', '.join(
                            [verb.name + '.Event.' + event.upper() for event in verb.attributes['statusCallbackEvent'].split(' ')]
                        )
                    ).encode('utf-8')
                    verb.attributes.pop('statusCallbackEvent')
                    self.specific_imports.add('import java.util.Arrays;')
            elif verb.name == 'Conference':
                self.java_enumize(verb, 'beep')
                self.java_enumize(verb, 'record')
                if 'statusCallbackEvent' in verb.attributes:
                    verb.attributes['statusCallbackEvents'] = 'Arrays.asList({})'.format(
                        ', '.join(
                            ['Conference.Event.' + event.upper() for event in verb.attributes['statusCallbackEvent'].split(' ')]
                        )
                    ).encode('utf-8')
                    verb.attributes.pop('statusCallbackEvent')
                    self.specific_imports.add('import java.util.Arrays;')
            # Clean variables, attributes and imports for SSML methods
            elif verb.name == 'SsmlBreak':
                self.java_enumize(verb, 'strength')
            elif verb.name == 'SsmlPhoneme':
                self.java_enumize(verb, 'alphabet')
            elif verb.name == 'SsmlSayAs':
                if 'interpret-as' in verb.attributes:
                    verb.attributes['interpretAs'] = verb.attributes.pop('interpret-as')
                self.java_enumize(verb, 'interpretAs')
                self.java_enumize(verb, 'role')
            elif verb.name == 'SsmlEmphasis':
                self.java_enumize(verb, 'level')

    def java_enumize(self, verb, attr_name):
        if attr_name in verb.attributes and not isinstance(verb.attributes[attr_name], bytes):
            attr_value = [
                verb.name,
                pascalize(attr_name),
                underscore(verb.attributes[attr_name]).upper().replace('.', '_')
            ]
            verb.attributes[attr_name] = '.'.join(attr_value).encode('utf-8')

    def clean_python_specificities(self):
        """Python library specificities which requires to change the TwiML IR."""
        for verb, event in self.twimlir:
            if verb.is_ssml:
                verb.name = f'ssml_{verb.name}'
            if 'from' in verb.attributes:
                verb.attributes['from_'] = verb.attributes.pop('from')
            if verb.name == 'Play' and not verb.text:
                verb.text = ' '
            for name, value in verb.attributes.items():
                if value in ['true', 'false']:
                    verb.attributes[name] = pascalize(value).encode('utf-8')

    def clean_csharp_specificities(self):
        """C# library specificities which requires to change the TwiML IR."""
        for verb, event in self.twimlir:
            if verb.is_ssml:
                verb.name = pascalize(f'ssml_{verb.name}')
            if verb.name == 'Play' and not verb.text:
                verb.text = ' '
            elif verb.name == 'Redirect' and self.twimlir.is_messaging_response:
                verb.attributes['url'] = verb.text
                verb.text = None
            elif verb.name == 'say-as':
                interpret_as = verb.attributes.get('interpret-as')
                if interpret_as:
                    verb.attributes['interpretAs'] = interpret_as
                    verb.attributes.pop('interpret-as')

    def clean_ruby_specificities(self):
        """Ruby library specificities which requires to change the TwiML IR."""
        for verb, event in self.twimlir:
            if verb.name == 'Play' and verb.text:
                verb.attributes['url'] = verb.text
                verb.text = None
            elif verb.name == 'Message' and verb.text:
                verb.attributes['body'] = verb.text
                verb.text = None
            elif verb.name == 'Dial' and verb.text:
                verb.attributes['number'] = verb.text
                verb.text = None
            elif verb.name == 'say-as':
                verb.name = 'say_as'
            # the `message` is optional and should be passed as a keyword argument
            elif verb.name == 'Say':
                if verb.text:
                    verb.attributes['message'] = verb.text
                    verb.text = ''

    def clean_node_specifities(self):
        for verb, event in self.twimlir:
            if verb.is_ssml:
                verb.name = camelize(f'ssml_{verb.name}')

    def write_code(self):
        """Write the code in the generator file."""
        if self.code_filepath.exists():
            self.code_filepath.unlink()
        self.code_filepath.write_text(str(self), encoding='utf-8')
        self.format_code()

    def format_code(self):
        if 'formatter' not in self.language_spec:
            return
        format_cmd = self.language_spec['formatter'].format(filepath=str(self.code_filepath))
        subprocess.run([format_cmd], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Constants for verify result
    VERIFY_SUCCESS = 0
    VERIFY_FAILURE = 1
    VERIFY_COMPILE_ERROR = 2

    def verify(self):
        """Try to run the code and verify its output against the original TwiML."""
        parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, strip_cdata=True)
        if self.language_spec['language'] == 'java':
            p = self.verify_java()
        elif self.language_spec['language'] == 'csharp':
            p = self.verify_csharp()
        else:
            p = self.verify_generic()

        if p.returncode == 0:
            input_tree = etree.parse(str(self.twiml_filepath), parser)
            output_tree = etree.fromstring(p.stdout, parser)
            comparison_result = self.etree_element_eq(input_tree.getroot(), output_tree)
            return (
                TwimlCodeGenerator.VERIFY_SUCCESS if comparison_result else TwimlCodeGenerator.VERIFY_FAILURE,
                '\n'.join([p.stdout.decode(), p.stderr.decode()]),
                etree.tostring(input_tree, encoding='utf-8', pretty_print=True).decode(),
                etree.tostring(output_tree, encoding='utf-8', pretty_print=True).decode()
            )
        else:
            return (
                TwimlCodeGenerator.VERIFY_COMPILE_ERROR,
                '\n'.join([p.stdout.decode(), p.stderr.decode()]),
                None,
                None
            )

    def verify_generic(self):
        generic_command = [self.language_spec['language'], str(self.code_filepath)]
        logger.debug('Running: {}'.format(' '.join(generic_command)))
        return subprocess.run(generic_command,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def verify_java(self):
        if not shutil.which('java'):
            raise Exception('You need to install java if you want to verify a java file')

        example_filepath = Path('Example.java')
        class_filepath = Path('Example.class')
        jar_filepath = self.lib_filepath / 'twilio-7.22.0-jar-with-dependencies.jar'

        def java_cleanup():
            try:
                example_filepath.unlink()
                class_filepath.unlink()
            except OSError:
                pass

        javac_command = ['javac', '-cp', str(jar_filepath), 'Example.java']
        java_command = ['java', '-cp', str(jar_filepath) + ':', 'Example']

        shutil.copy(str(self.code_filepath), str(example_filepath))

        logger.debug('Running : {}'.format(' '.join(javac_command)))
        p = subprocess.run(javac_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if p.returncode != 0:
            java_cleanup()
            return p

        logger.debug('Running : {}'.format(' '.join(java_command)))
        p = subprocess.run(java_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        java_cleanup()
        return p

    def verify_csharp(self):
        if not shutil.which('dotnet'):
            raise Exception('You need to install dotnet core if you want to verify a C# file')

        is_new_env = False
        cwd = Path.cwd()
        project_filepath = Path('dotnet_env')
        if not project_filepath.exists():
            project_filepath.mkdir()
            is_new_env = True
        os.chdir(project_filepath)

        def csharp_clean():
            try:
                os.chdir(cwd)
            except OSError:
                pass

        dotnet_new_command = ['dotnet', 'new', 'console']
        dotnet_add_package_command = ['dotnet', 'add', 'package', 'Twilio']
        dotnet_run_command = ['dotnet', 'run']

        if is_new_env:
            logger.debug('Running: {}'.format(' '.join(dotnet_new_command)))
            p = subprocess.run(dotnet_new_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if p.returncode != 0:
                csharp_clean()
                return p

            logger.debug('Running: {}'.format(' '.join(dotnet_add_package_command)))
            p = subprocess.run(dotnet_add_package_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if p.returncode != 0:
                csharp_clean()
                return p

        program_path = Path('Program.cs')
        program_path.unlink()
        program_path.symlink_to(self.code_filepath)

        logger.debug('Running: {}'.format(' '.join(dotnet_run_command)))
        p = subprocess.run(dotnet_run_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        csharp_clean()
        return p

    def etree_element_eq(self, a, b):
        """Return True if two etree (a and b) are equal."""
        return (a.tag == b.tag
                and a.tail == b.tail
                and a.attrib == b.attrib
                and (TwimlIR.clean_text(a.text) == TwimlIR.clean_text(b.text)
                     if a.text and b.text else a.text == b.text)
                and len(a) == len(b)
                and all(self.etree_element_eq(c1, c2) for c1, c2 in zip(a, b)))
