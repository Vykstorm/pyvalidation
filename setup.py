
'''
Installation script
'''

from setuptools import setup


if __name__ == '__main__':
    setup(
        name = 'vpfargs',
        version = '1.0.0',
        description = 'A small python module that is aimed to provide a simple mechanism for function arguments validation and parsing',
        author = 'Vykstorm',
        author_email = 'victorruizgomezdev@gmail.com',
        python_requires = '>=2.7',
        install_requires = [],
        dependency_links = [],
        py_modules= ['vpfargs'],
        keywords = ['validation', 'parsing', 'decorators']
    )