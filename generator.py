#!/usr/bin/env python
# coding: utf-8
from twiml_code_generator import TwimlCodeGenerator


if __name__ == '__main__':
    code_generator = TwimlCodeGenerator('assets/message_media.xml', language='python')
    code_generator.write_code()
    code_generator.verify()
    print('')
    print(' CODE GENERATED '.center(80, '='))
    print(code_generator)
    print('=' * 80)
    print('Written at {}'.format(code_generator.code_filepath))
