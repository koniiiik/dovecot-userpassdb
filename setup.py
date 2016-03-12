# Based on the sample setuptools setup module.
# https://packaging.python.org/en/latest/distributing.html
# https://github.com/pypa/sampleproject

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='dovecot-userpassdb',
    version='0.1.0',
    description='Dovecot user-controllable passwords',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/koniiiik/dovecot-userpassdb',

    # Author details
    author='Michal Petrucha',
    author_email='michal.petrucha@koniiiik.org',

    # Choose your license
    license='BSD',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: System Administrators',
        'Topic :: Communications :: Email :: Post-Office :: IMAP',
        'Topic :: Communications :: Email :: Post-Office :: POP3',
        'Topic :: System :: Systems Administration :: Authentication/Directory',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: BSD License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',

        'Operating System :: POSIX',
    ],
    keywords='dovecot imap password checkpassword',
    py_modules=["dovecot_userpassdb"],
    install_requires=['passlib'],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
        'test': ['nose2'],
    },

    entry_points={
        'console_scripts': [
            'dovecot-checkpass=dovecot_userpassdb:'
                'UserPassDBEntry.checkpass_main',
            'imap-passwd=dovecot_userpassdb:'
                'UserPassDBEntry.change_password',
        ],
    },
)
