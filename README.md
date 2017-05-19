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

You can use `./generator.py` to print out code from a TwiML file

```bash
$ ./generator.py assets/call_on_hold.xml -l python
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

## License
MIT
