#!/usr/bin/env python
# coding: utf-8
import logging

from lxml import etree
from pathlib import Path

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class TwimlAttributesTypes(dict):
    """Class to handle attributes for TwiML verbs."""

    def __init__(self, xsd_filepath=None):
        """Construct an object to handle TwiML attributes types."""
        self.xsd_filepath = self.get_xsd_filepath(xsd_filepath)
        self.build_attributes_types()

    def get_xsd_filepath(self, xsd_filepath):
        """Return the path to the XSD file cast as a Path instance."""
        if isinstance(xsd_filepath, Path):
            return xsd_filepath
        elif not xsd_filepath:
            return Path(__file__).parent / 'xsd' / 'twiml_v20100401_twilioRealtimeCallSchema.xsd'
        else:
            return Path(xsd_filepath)

    def build_attributes_types(self):
        """Fill a dict of expect types for TwiML attributes."""
        tree = etree.parse(str(self.xsd_filepath))
        for complexType in tree.iter("{http://www.w3.org/2001/XMLSchema}complexType"):
            if 'name' not in complexType.attrib:
                continue
            complexTypeName = complexType.attrib['name']
            attributes_types = {}
            for attribute in complexType.iter('{http://www.w3.org/2001/XMLSchema}attribute'):
                attributes_types[attribute.attrib['name']] = attribute.attrib['type']
            self[complexTypeName] = attributes_types


class TwimlIR(object):
    """Internal Representation of a TwiML."""

    def __init__(self, xml_filepath=None):
        self.xml_filepath = self.__class__.get_xml_filepath(xml_filepath)
        self.twiml_attributes_types = TwimlAttributesTypes()
        self.response = None
        self.is_voice_response = True
        self.generated_variables_names = set()

        logger.debug('Parsing XML: {}'.format(self.xml_filepath))
        self.parse_xml()

    @staticmethod
    def get_xml_filepath(xml_filepath):
        """Return the path to a XML file cast as a Path instance."""
        if isinstance(xml_filepath, Path):
            return xml_filepath
        elif not xml_filepath:
            return Path(__file__).resolve().parent.parent / 'assets' / 'gather_advanced.xml'
        else:
            return Path(xml_filepath)

    @property
    def is_messaging_response(self):
        """True if the TwiML is for Messaging."""
        return not self.is_voice_response

    def parse_xml(self):
        """Parse the TwiML file and create the internal representation."""
        latest_verb = None
        processing_ssml = False
        for event, twiml_verb in etree.iterparse(str(self.xml_filepath), events=("start", "end")):
            if event == 'start':
                logger.debug('Start event on verb : {}'.format(twiml_verb.tag))
                verb = TwimlIRVerb(
                    name=twiml_verb.tag,
                    attributes=self.clean_attributes(twiml_verb.tag, twiml_verb.attrib),
                    text=self.clean_text(twiml_verb.text),
                    parent=latest_verb,
                    tail=twiml_verb.tail,
                    is_ssml=processing_ssml
                )
                if twiml_verb.tag == 'Say' and len(list(twiml_verb)) > 0:
                    processing_ssml = True
                if twiml_verb.tag == 'Message':
                    self.is_voice_response = False
                if twiml_verb.tag == 'Response':
                    self.response = verb
                else:
                    latest_verb.children.append(verb)
                latest_verb = verb
                logger.debug('Set Latest Verb Seen as : {}'.format(latest_verb.name))

            elif event == 'end':
                logger.debug('End event on verb : {}'.format(twiml_verb.tag))
                latest_verb = latest_verb.parent
                if latest_verb:
                    logger.debug('Set Latest Verb Seen as : {}'.format(latest_verb.name))
                if twiml_verb.tag == 'Say' and len(list(twiml_verb)) > 0:
                    processing_ssml = False

    @staticmethod
    def clean_text(text):
        """Remove unecessary blank space from the text and keep a newline in between."""
        return (
            None if text is None or text.strip() == ''
            else '\\n'.join(line.strip() for line in text.strip().split('\n'))
        )

    def clean_attributes(self, verb, attributes):
        """Cast attributes value to the proper type."""
        verb_type = verb + 'Type'
        if verb_type not in self.twiml_attributes_types:
            return attributes

        cleaned_attributes = {}
        attributes_types = self.twiml_attributes_types[verb_type]
        for name, value in attributes.items():
            if name in attributes_types and attributes_types[name] == 'xs:int':
                value = int(value)
            cleaned_attributes[name] = value
        return cleaned_attributes

    def __iter__(self):
        """Iterator to traverse the TwiML IR with a DFS."""
        visited, queue = set(), [(self.response, 'start')]
        while queue:
            verb, event = queue.pop()
            visited.add(verb)
            if event == 'start':
                queue.append((verb, 'end',))
                queue.extend(
                    [
                        (v, 'start')
                        if not v.is_leaf else (v, 'leaf')
                        for v in reversed(verb.children)
                    ]
                )
            yield verb, event

    def reverse_iter(self):
        """Iterator to traverse the TwiML IR from leaves to parent."""
        verb = self.response
        visited, queue = set(), []
        while not verb.is_leaf:
            verb = verb.children[0]

        queue.append(verb)
        while queue:
            verb = queue.pop()
            if verb in visited:
                continue
            elif verb.children and len(set(verb.children) & visited) < len(verb.children):
                queue.extend(verb.children)
                continue
            if verb.parent:
                queue.append(verb.parent)
                queue.extend(verb.siblings)
            visited.add(verb)
            yield verb

    def get_verb_names(self, exclude_ssml_verbs=True):
        """Return a set of all verbs used."""
        verb_names = set()
        for verb, event in self:
            if exclude_ssml_verbs and verb.is_ssml:
                continue
            verb_names.add(verb.name)
        return sorted(list(verb_names))


class TwimlIRVerb(object):
    """Internal Representation of a TwiML verb."""

    def __init__(self, name, attributes, text, parent, tail, is_ssml):
        self.name = name.replace('-', '_')
        self.attributes = dict(attributes)
        self.text = text
        self.parent = parent
        self.tail = tail
        self.is_ssml = is_ssml

        self.children = []

        self.depth = 0
        if self.parent:
            self.depth = self.parent.depth + 1
        self.variable_name = None

    @property
    def is_leaf(self):
        return len(self.children) == 0

    def __repr__(self):
        attributes_string = ' '.join(
            ['{}={}'.format(name, repr(value)) for name, value in self.attributes.items()]
        )
        if len(attributes_string) > 0:
            attributes_string = ' ' + attributes_string
        text_string = '({})'.format(self.text) if self.text else ''
        return '<{name}{attributes_string}>{text_string}'.format(
            name=self.name,
            attributes_string=attributes_string,
            text_string=text_string
        )

    def add_child(self, name, text):
        newVerb = TwimlIRVerb(
            name=name,
            attributes={},
            text=text,
            parent=self
        )
        self.children.append(newVerb)

    @property
    def siblings(self):
        """Return a set of all other siblings without this node."""
        siblings = set(self.parent.children)
        siblings.remove(self)
        return siblings


if __name__ == '__main__':
    for verb in TwimlIR().reverse_iter():
        print('{padding}{verb}'.format(padding='  ' * verb.depth, verb=verb))
