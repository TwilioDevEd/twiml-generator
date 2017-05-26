from setuptools import setup

setup(name='twiml-generator',
      version='0.1',
      description='Generate a code from a TwiML file',
      url='https://github.com/TwilioDevEd/twiml-generator/',
      author='Samuel Mendes',
      author_email='smendes@twilio.com',
      license='MIT',
      packages=['twiml_generator'],
      include_package_data=True,
      install_requires=[
          'lxml',
          'inflection',
          'yapf'
      ],
      zip_safe=False)