from typing import Type

from twiml_generator.specificity.csharp import CSharp
from twiml_generator.specificity.java import Java
from twiml_generator.specificity.node import Node
from twiml_generator.specificity.php import PHP
from twiml_generator.specificity.python import Python
from twiml_generator.specificity.ruby import Ruby


class Specificities:
    """All languages specificities cleaner"""

    def __init__(self):
        self.__languages = [Java, CSharp, Node, PHP, Python, Ruby]

    def clean(self, generator, language):
        for lang in self.__languages:
            if language == lang.__name__.lower():
                lang.clean(generator)
