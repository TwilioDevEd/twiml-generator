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

## Installation

Create a Python virtual environment:

```
python3 -m venv venv
```

Activate the environment and install requirements:

```
source venv/bin/activate
pip install -r requirements.txt
```

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

### Installation Steps (MacOS)

#### Python

Following the install instructions for this tool will also install the required Twilio helper library.

#### C#

Download .Net Core from [Microsoft](https://dotnet.microsoft.com/download/dotnet-core)
and follow the .Net Core package installation instructions.

#### Java

Install Java with homebrew. (The instructions below install java8.)

```
brew tap adoptopenjdk/openjdk
brew install adoptopenjdk/openjdk/adoptopenjdk8 --cask
```

Download the Twilio helper library jar from [maven central](https://mvnrepository.com/artifact/com.twilio.sdk/twilio)

Create a `lib` folder in the top level of this repository, and move the
Twilio helper library jar into it.

#### Ruby

On MacOS, it's helpful to use a Ruby manager to install Gems, instead of
using `sudo` to install gems to the system ruby.

Using [rbenv](https://github.com/rbenv/rbenv):

```
brew install rbenv
rbenv init
```

Follow the instructions printed out from `rbenv init` for setting up the `rbenv` shell integration.

**NOTE**: You must also add the output of `rbenv init` to your `~/.bash_profile`, even if you use another
shell, such as `.zsh`. The `generator` script uses Python's `subprocess` module, which will
only load your `bash_profile` to run commands.

Then, install your desired ruby version and the Twilio helper library:

```
rbenv install 2.6.3  # or other preferred version; the twilio helper library works with ruby >1.9.3
rbenv global 2.6.3  # or whichever version you installed
rbenv rehash  # installs shims -- run this after installing a new ruby version with rbenv
gem update --system  # update the RubyGems system software
gem install twilio-ruby
```

#### PHP

Install PHP and Composer with homebrew:

```
brew install php
brew install composer
```

Install the Twilio helper library with `composer` (this will create `composer.json` and `composer.lock` files).

```
composer require twilio/sdk
```

#### Node

Install node using homebrew and then install the Twilio helper library with `npm`:

```
brew install node
npm install twilio
```

## License
MIT
