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
| [twilio-ruby](https://github.com/twilio/twilio-ruby/) | ? |


## Requirements
The generator tool will try to test the generated snippets using a local
environment for every language's SDK version.

In order to use the testing functionality, you need to install each Helper Library. 

### Helper Library Installation
<details>
  <summary>Click to expand</summary>

#### twilio-csharp

- [twilio-csharp GitHub Repo](https://github.com/twilio/twilio-csharp/)
- Requirements: 
  - .NET Core 1.0+
- Installation: 
  - From within this project's root directory, run the following command: 
  ```bash
  dotnet add package Twilio
  ```
  
#### twilio-java

- [twilio-java GitHub Repo](https://github.com/twilio/twilio-java)
- Requirements: 
  - Java 8
  - Maven
    - I think you can install this with Homebrew? 
    
    ```bash
    brew cask install java
    brew install maven
    ```
- Installation: 
  - Download `.jar` file for the desired version of Twilio SDK
    1. Go to [mvnrepository.com](https://mvnrepository.com/artifact/com.twilio.sdk/twilio) and click on the version of the Helper Library you need. 
    1. In the table at the top of the page, find **Files** and click on **jar** (may need to click on **View All** and select the `twilio-<version number>-jar-with-dependencies.jar` file?)
    1. Place the `.jar` file in this project's `./lib/` directory.

#### twilio-python

- [twilio-python GitHub Repo](https://github.com/twilio/twilio-python)
- Requirements: 
  - Python 3.7+
- Installation: 
  - Install `twilio` sdk with `pip` (already in requirements.txt)
  (does this work with pip3? idk)

  ```bash
  pip3 install twilio
  ```

#### twilio-ruby

- [twilio-ruby GitHub Repo](https://github.com/twilio/twilio-ruby)

- Requirements: 
  - Ruby 3.1
  - RubyGems

- Installation: 
  - Install ruby and `twilio-ruby` gem
  - (In the root ?)

  ```bash
  gem install twilio-ruby -v 5.76.0
  ```

#### twilio-php

- [twilio-php GitHub Repo](https://github.com/twilio/twilio-php/)
- Requirements: 
  - PHP 8
  - [Composer](https://getcomposer.org/download/)
- Installation: 
  - In the root directory of this project, run the following command: 
  ```bash
  composer require twilio/sdk
  ```

#### twilio-node

- [twilio-node GitHub Repo](https://github.com/twilio/twilio-node/)
- Requirements: 
  - Node.js 14+
- Installation: 
  - In the root directory of this project, run the following command: 
    
  ```bash
  npm install twilio
  ```

#### twilio-go (Coming soon?)

- [twilio-go GitHub Repo](https://github.com/twilio/twilio-go)

</details>

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
- :warning: Unfortunately, the Helper Libraries don't do any sort of enforcement around required or associated attributes. You will only be made aware of errors once Twilio executes the TwiML on a live call. Therefore: 
  - Make sure that you are including any required attributes and/or a body if necessary. 
  - If any attribute implies the use of another attribute, make sure to include it in the example. E.g. You wouldn't/shouldn't use `statusCallbackEvent` without also using the `statusCallback` attribute. 
  - Don't force errors onto our customers. Not sure if the TwiML actually works? Hook up a Twilio Phone Number to a TwiML Bin and test it out yourself.

:warning: When you add the TwiML file to the [api-snippets repo](https://github.com/TwilioDevEd/api-snippets/tree/master/twiml), you need to change the file extension to `.twiml`. 

### Generate the Helper Library code via the command line

  You can generate the Helper Library code by running the `generator.py` file.

  In your terminal, run a command with following format: 
  
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
# TODO: ADD other helper libraries to code_generator.verify?
code_generator.verify()
```

## Updating the project for new Helper Library Versions

(Coming soon)

## License
MIT
