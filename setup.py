"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

from os import path

# Always prefer setuptools over distutils
from setuptools import setup, find_packages

import whpool

here = path.abspath(path.dirname(__file__))

setup(
    name='whpool',
    version=whpool.VERSION,
    description='WHCA Pool Reports Utilities',
    long_description='Utilities for processingn WHCA Pool Reports',
    url='https://github.com/umd-lib/whpool',
    author='University of Maryland Libraries',
    author_email='lib-ssdr@umd.edu',

    # Classifiers help users find your project by categorizing it.
    #
    # For a list of valid classifiers, see
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        'Environment :: Console',

        # Indicate who your project is intended for
        'Intended Audience :: Information Technology',
        'Topic :: Utilities',

        # Pick your license as you wish
        'License :: OSI Approved :: Apache Software License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3 :: Only',
    ],

    # This field adds keywords for your project which will appear on the
    # project page. What does your project relate to?
    #
    # Note that this is a string of words separated by whitespace, not a list.
    keywords='WHCA',

    # You can just specify package directories manually here if your project is
    # simple. Or you can use find_packages().
    #
    # Alternatively, if you just want to distribute a single Python file, use
    # the `py_modules` argument instead as follows, which will expect a file
    # called `my_module.py` to exist:
    #
    #   py_modules=["my_module"],
    #
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    # This field lists other packages that your project depends on to run.
    # Any package you put here will be installed by pip when your project is
    # installed, so they must be valid existing projects.
    #
    # For an analysis of "install_requires" vs pip's requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[
        'beautifulsoup4',
        'click',
        'codetiming',
        'html_sanitizer',
        'PyYAML',
        'requests'
    ],
    python_requires='>=3.9',

    # List additional groups of dependencies here (e.g. development
    # dependencies). Users will be able to install these using the "extras"
    # syntax.
    #
    # Similar to `install_requires` above, these must be valid existing
    # projects.
    extras_require={  # Optional
       'dev': ['pycodestyle', 'mypy'],
       'test': ['pytest', 'pytest-cov'],
    },

    # If there are data files included in your packages that need to be
    # installed, specify them here.
    #
    # If using Python 2.6 or earlier, then these have to be included in
    # MANIFEST.in as well.
    # package_data={  # Optional
    #    'config': ['logging.yml'],
    # },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # `pip` to create the appropriate form of executable for the target
    # platform.
    entry_points={
        'console_scripts': [
            'whpool=whpool.cli:main',
        ],
    },

    # List additional URLs that are relevant to your project as a dict.
    #
    # This field corresponds to the "Project-URL" metadata fields:
    # https://packaging.python.org/specifications/core-metadata/#project-url-multiple-use
    #
    # Examples listed include a pattern for specifying where the package tracks
    # issues, where the source is hosted, where to say thanks to the package
    # maintainers, and where to support the project financially. The key is
    # what's used to render the link text on PyPI.
    project_urls={
        'Source': 'https://github.com/umd-lib/whpool',
    },
)
