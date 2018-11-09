#!/usr/bin/env python
# coding: utf-8
from twiml_generator import TwimlCodeGenerator
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("twiml_filepath", help="Path to a TwiML file")
    parser.add_argument("-l", "--language", help="Language for the code to generate",
                        choices=['csharp', 'java', 'node', 'php', 'python', 'ruby'])
    parser.add_argument("--verify",  action='store_false', help="Only runs the verification")
    args = parser.parse_args()

    code_generator = TwimlCodeGenerator(args.twiml_filepath, language=args.language)
    if args.verify:
        code_generator.write_code()
        print(' CODE GENERATED '.center(80, '='))
        print(code_generator)
        print('=' * 80)
        print('Written at {}'.format(code_generator.code_filepath))
    print('Running verification on %s:' % code_generator.code_filepath, end='')
    result, stdout, input_tree, output_tree = code_generator.verify()
    if result == TwimlCodeGenerator.VERIFY_SUCCESS:
        print(' \x1B[92m[passed]\x1B[39m')
    elif result == TwimlCodeGenerator.VERIFY_FAILURE:
        print(' \x1B[91m[failed]\x1B[39m')
        print('INPUT:\n' + input_tree)
        print('OUTPUT:\n' + output_tree)
    else:
        print(' \x1B[91m[error]\x1B[39m')
        print(stdout)
