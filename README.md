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


<!-- TODO  -->
Create file set that is properly-structured for api-snippets/twiml
- enter a filename (kebab-cased) that describes the example
- create a directory w/ filename
- create a sub-directory called output
- create a file called <filename> with `.twiml` extension
- enter TwiML 
- put into `.twiml` file
- create `meta.json` file
- enter `title` / description
- put `title` into `meta.json` file
- run generator.py for each helper library and output into directory


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
# TODO: ADD other helper libraries to code_generator?
code_generator.verify()
```

## Requirements
The generator tool will try to test the generated snippets using a local
environment for every language's SDK version.

In order to use the testing functionality, you need to install each Helper Library. 

### Helper Library Installation

TODO: Instructions for how to check if you have these things installed? 

#### twilio-csharp

[twilio-csharp GitHub Repo](https://github.com/twilio/twilio-csharp/)

Requirements: 
  - .NET Core 1.0+
 
Installation: 
  - From within this project's root directory, run the following command: 
    ```bash
    dotnet add package Twilio
    ```
  
#### twilio-java

[twilio-java GitHub Repo](https://github.com/twilio/twilio-java)

Requirements: 
- Java 8
- Maven
  - I think you can install this with Homebrew? 
    
    ```bash
    brew cask install java
    brew install maven
    ```

Installation: 
  - Download `.jar` file for the desired version of Twilio SDK
    1. Go to [mvnrepository.com](https://mvnrepository.com/artifact/com.twilio.sdk/twilio) and click on the version of the Helper Library you need. 
    1. In the table at the top of the page, find **Files** and click on **jar** (may need to click on **View All** and select the `twilio-<version number>-jar-with-dependencies.jar` file?)
    1. Place the `.jar` file in this project's `./lib/` directory.

#### twilio-python

[twilio-python GitHub Repo](https://github.com/twilio/twilio-python)

Requirements: 
  - Python 3.7+

Installation: 
  - Install `twilio` sdk with `pip` (already in requirements.txt)
  (does this work with pip3? idk)

  ```bash
  pip3 install twilio
  ```

#### twilio-ruby

[twilio-ruby GitHub Repo](https://github.com/twilio/twilio-ruby)

Requirements: 
  - Ruby 3.1
  - RubyGems

Installation: 
  - Install ruby and `twilio-ruby` gem
  - (In the root ?)

    ```bash
    gem install twilio-ruby -v 5.76.0
    ```

#### twilio-php

[twilio-php GitHub Repo](https://github.com/twilio/twilio-php/)

Requirements: 
- PHP 8
- [Composer](https://getcomposer.org/download/)

Installation: 
  - In the root directory of this project, run the following command: 
  ```bash
  composer require twilio/sdk
  ```

#### twilio-node

[twilio-node GitHub Repo](https://github.com/twilio/twilio-node/)

Requirements: 
  - Node.js 14+

Installation: 
  - In the root directory of this project, run the following command: 
    
    ```bash
    npm install twilio
    ```

#### twilio-go (Coming soon?)

[twilio-go GitHub Repo](https://github.com/twilio/twilio-go)


## Updating the project for new Helper Library Versions

(Coming soon)

## License
MIT
