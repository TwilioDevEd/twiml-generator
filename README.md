<a href="https://www.twilio.com">
  <img src="https://static0.twilio.com/marketing/bundles/marketing/img/logos/wordmark-red.svg" alt="Twilio" width="250" />
</a>

# TwiML Generator
A tool to help generate sample code for creating TwiML with Twilio's Helper Libraries

## Supported Helper Library Versions

| Helper Library  | Version |
| :-------------  |:------------- |
| [twilio-csharp](https://github.com/twilio/twilio-csharp/) | 5.x |
| [twilio-java](https://github.com/twilio/twilio-java/) | 7.x |
| [twilio-node](https://github.com/twilio/twilio-node/) | 3.x |
| [twilio-php](https://github.com/twilio/twilio-php/) | 5.x |
| [twilio-python](https://github.com/twilio/twilio-python/) | 6.x |
| [twilio-ruby](https://github.com/twilio/twilio-ruby/) | 5.x |


## Requirements
The generator tool will try to test the generated snippets using a local
environment for every language's SDK version.

In order to use the testing functionality, you need to install each Helper Library. 

### Helper Library Installation
<details>
  <summary>Click to see installation instructions for each Helper Library and related dependencies</summary>

#### twilio-csharp

- [twilio-csharp GitHub Repo](https://github.com/twilio/twilio-csharp/)
- Requirements: 
  - [.NET Core 1.0+](https://dotnet.microsoft.com/download/dotnet-core)
- `twilio-csharp` installation: 
  - From within this project's root directory run the following command: 
    ```bash
    dotnet add package Twilio
    ```
  
#### twilio-java

- [twilio-java GitHub Repo](https://github.com/twilio/twilio-java)
- Requirements: 
  - Java 8
    
    To install Java 8, run the following command: 
    
    ```bash
    brew tap adoptopenjdk/openjdk
    brew install adoptopenjdk/openjdk/adoptopenjdk8 --cask
    ```

- `twilio-java` installation: 

    1. Go to [mvnrepository.com](https://mvnrepository.com/artifact/com.twilio.sdk/twilio) and click on the version of the Helper Library you need. 
    1. In the table at the top of the page, find **Files** and click on **jar** (may need to click on **View All** and select the `twilio-<version number>-jar-with-dependencies.jar` file?)
    1. Create a `lib` directory in the root of this project and place the `.jar` file in it.

#### twilio-python

- [twilio-python GitHub Repo](https://github.com/twilio/twilio-python)
- Requirements: 
  - Python 3.7+

- `twilio-python` installation: 
  
  - Install `twilio` sdk with `pip` 
  
    (**Note:** If you followed the Installation instructions for this repo, `twilio-python` is already installed!)

    ```bash
    pip3 install twilio
    ```

#### twilio-ruby

- [twilio-ruby GitHub Repo](https://github.com/twilio/twilio-ruby)

- Requirements: 
  - Ruby 3.1 and [rbenv](https://github.com/rbenv/rbenv)

    To install `rbenv`, run the following command: 

      ```bash
      brew install rbenv
      rbenv init
      ```
      Follow the instructions printed out from rbenv init for setting up the rbenv shell integration.

      **NOTE:** You must also add the output of `rbenv init` to your `~/.bash_profile`, even if you use another shell, such as `.zsh`. The generator script uses Python's subprocess module, which will only load your `bash_profile` to run commands.

      Then, install your desired Ruby version:

      ```bash
      rbenv install 2.6.3  # or other preferred version; the twilio-ruby works with ruby >1.9.3
      rbenv global 2.6.3  # or whichever version you installed
      rbenv rehash  # installs shims -- run this after installing a new ruby version with rbenv
      gem update --system  # update the RubyGems system software
      ```

- `twilio-ruby` installation: 

  Run the following command: 

  ```bash
  gem install twilio-ruby
  ```

  or install a specific `twilio-ruby` version: 

  ```bash
  gem install twilio-ruby -v 5.76.0
  ```

#### twilio-php

- [twilio-php GitHub Repo](https://github.com/twilio/twilio-php/)
- Requirements: 
  - PHP 8
    
    To install PHP 8, run the following command: 
    ```
    brew install php
    ```

  - [Composer](https://getcomposer.org/download/)
    
    Run the following command: 
    
    ```bash
    brew install composer
    ```

- `twilio-php` installation: 

  In the root directory of this project, run the following command: 
  
  ```bash
  composer require twilio/sdk
  ```
  This will create `composer.json` and `composer.lock` files.

#### twilio-node

- [twilio-node GitHub Repo](https://github.com/twilio/twilio-node/)
- Requirements: 
  - Node.js 14+
  
    To install Node.js, run the following command: 
  
    ```bash
    brew install node
    ```

- `twilio-node` installation: 

  In the root directory of this project, run the following command: 
    
  ```bash
  npm install twilio
  ```

#### twilio-go (Coming soon?)

[twilio-go GitHub Repo](https://github.com/twilio/twilio-go)

</details>

## Installation

Create a Python virtual environment:

```bash
python3 -m venv venv
```

Activate the environment and install requirements:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

## Use the tool to create and/or verify Helper Library code

You can run the tool via the command line or use it as a Python library. 

For either option, you first need to create a TwiML file. 

### Create a `.xml` file containing the TwiML for which you want to generate Helper Library code. 

- Include the XML declaration line at the top of the file. 

  ```xml
  <?xml version="1.0" encoding="UTF-8"?>
  ```

- `<Response>` and `</Response>` tags must be present. 
- Use `example.com` domains for any sample URLs. 
- :warning: Unfortunately, the Helper Libraries don't do any sort of enforcement around required or associated attributes. You will only be made aware of errors once Twilio executes the TwiML (e.g. during a call). Therefore: 
  - Make sure that you are including any required attributes and/or a body if necessary. 
  - If any attribute implies the use of another attribute, make sure to include it in the example. E.g. You wouldn't/shouldn't use `statusCallbackEvent` without also using the `statusCallback` attribute. 
  - Don't force errors onto our customers. Not sure if the TwiML actually works? Hook up a Twilio Phone Number to a TwiML Bin and test it out yourself.

:warning: When you add the TwiML file to the [api-snippets repo](https://github.com/TwilioDevEd/api-snippets/tree/master/twiml), you need to change the file extension to `.twiml`. 

### Generate the Helper Library code via the command line

  You can generate the Helper Library code by running the `generator.py` file.

  In your terminal, run a command with the following format: 
  
  `./generator.py <your .xml filepath> -l <Helper Library language>`
  
  #### Languages

  The `-l` option specifies the Helper Library for which you wish to generate code. The allowed values are: 
  - `python` 
  - `ruby`
  - `csharp`
  - `java`
  - `php`
  - `node`
  
  Example: 
  ```bash
  ./generator.py assets/dial-basic.xml -l node
  ```

  #### Output location 

  By default, the tool outputs the Helper Library code into the `/generators/<Helper Library language>` directory. 

  You can specify an output location with the `-out` flag: 

  ```
  ./generator.py <your .twiml filepath> -out <output filepath> -l <Helper Library language>
  ```

  Example: 
  ```bash
  ./generator.py assets/dial-basic.xml -out ./assets/dial-basic/dial-basic.4.x.js -l node
  ```

  :warning: When you add the Helper Library code files to the [api-snippets repo](https://github.com/TwilioDevEd/api-snippets/tree/master/twiml), the file extension must include the Helper Library version, e.g. `some-example.4.x.js`.  


### Generate Messaging TwiML samples

The vast majority of TwiML verbs are for Voice. If you would like to create a new TwiML code sample for Messaging rather than for Voice, you can pass in the `--messaging` flag:


  `./generator.py <filepath of TwiML file> -out <filepath of code to verify> -l <Helper Library language> --messaging`

  
### Verify existing Helper Library code via the command line

This tool will automatically verify each code sample as it is created. You can also test an existing code sample without generating new sample code with the `--verify` flag. 

The format is:

  `./generator.py <filepath of TwiML file> -out <filepath of code to verify> -l <Helper Library language> --verify`

Example: 
```bash
./generator.py assets/call_on_hold.xml -out assets/call_on_hold.py -l python --verify
```

### Use the tool as a Python library

Below is a small example on how to use this tool in your Python code:

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

## Updating the project for new Helper Library Versions

(Coming soon)

## License
MIT
