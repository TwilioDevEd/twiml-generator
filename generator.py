#!/usr/bin/env python
# coding: utf-8
from twiml_generator import TwimlCodeGenerator
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("twiml_filepath", help="Path to a TwiML file")
    parser.add_argument("-l", "--language", help="Language for the code to generate",
                        choices=['csharp', 'java', 'node', 'php', 'python'])
    args = parser.parse_args()

    code_generator = TwimlCodeGenerator(args.twiml_filepath, language=args.language)
    code_generator.write_code()
    if args.language in ['node', 'php', 'python']:
        code_generator.verify()

    print('')
    print(' CODE GENERATED '.center(80, '='))
    print(code_generator)
    print('=' * 80)
    print('Written at {}'.format(code_generator.code_filepath))
