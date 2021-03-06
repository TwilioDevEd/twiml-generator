<a href="https://www.twilio.com">
  <img src="https://static0.twilio.com/marketing/bundles/marketing/img/logos/wordmark-red.svg" alt="Twilio" width="250" />
</a>

# TwiML Generator
A tool to help generate sample code for creating TwiML with Twilio's helper libraries

## Supported Languages

| Language  | SDK Version |
| :-------------  |:------------- |
| C# | 5.x |
| Java | 7.x |
| Node | 3.x |
| PHP | 5.x |
| Python | 6.x |

## Using the tool

You can use `./generator.py` to print out and save code that is generated from a TwiML file:

```bash
$ ./generator.py assets/call_on_hold.xml -l python
# optionally specify where the output file should be written. If not specified,
# it will be written to a /generators/<language> directory
$ ./generator.py assets/call_on_hold.xml -out assets/call_on_hold.py -l python
```

You can also skip the code generation and verify that an existing code sample correctly matches
the TwiML definition.

```bash
# the first file is the TwiML example, and the second file is the code to verify
$ ./generator.py assets/call_on_hold.xml -out assets/call_on_hold.py -l python --verify
```

## Using it as a Library

A small example on how to use it as a library in your Python code:

```python
from twiml_code_generator import TwimlCodeGenerator

my_twiml_file = 'assets/record_voicemail.xml'
code_generator = TwimlCodeGenerator(my_twiml_file, language='python')

# Print out the generated code
print(code_generator)

# Write a file with the generated code
code_generator.write_code()

# Run the generated code and verify the output xml against the source
# Only: Python, PHP, Node
code_generator.verify()
```

## Requirements
The generator tool will try to test the generated snippets using a local
environment for every language's SDK version.

* `csharp`: Install .NET Core
* `java`: Install Java and copy the current version of Twilio SDK jar
 file from maven central to `./lib/`
* `python`: Install `twilio` sdk with `pip` (already in requirements.txt)
* `ruby`: Install ruby and `twilio-ruby` gem
* `php`: Install php and `twilio/sdk` with `composer`
* `node`: Install node and `twilio` with `npm`

## License
MIT
