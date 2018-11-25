
'''
Installation script
'''

from setuptools import setup


if __name__ == '__main__':
    setup(
        name = 'pyvalidation',
        version = '1.0.0',
        description = 'A small python module that allows basic validation and parsing function arguments',
        author = 'Vykstorm',
        author_email = 'victorruizgomezdev@gmail.com',
        python_requires = '>=2.7',
        install_requires = [],
        dependency_links = [],
        keywords = ['validation', 'parsing', 'decorators']
    )