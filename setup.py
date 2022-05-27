# -*- coding: utf-8 -*-
import setuptools
import os

here = os.path.abspath(os.path.dirname(__file__))

description = 'Automatic documentation tool using Markdown and Python docstrings written with the numpydoc style'

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = description


with open(os.path.join(here, "requirements.txt"),"r") as f:
    requirements = [line.strip() for line in f.readlines()]

setuptools.setup(
    name="npdoc_to_md",
    version="2.0",
    license='The Unlicense',
    author="Thibault Bétrémieux",
    author_email="thibault.betremieux@gmail.com",
    url='https://github.com/ThibTrip/npdoc_to_md',
    download_url='https://github.com/ThibTrip/npdoc_to_md/archive/v2.0.tar.gz',
    keywords=['numpydoc','documentation', 'docstrings', 'python', 'markdown'],
    entry_points={'console_scripts': ['npdoc-to-md=npdoc_to_md.core:start_cli',
                                      # aliases (note that python-fire, the library
                                      # we use for the CLI also allows mixing "-"
                                      # and "_" in the same argument)
                                      'npdoc_to_md=npdoc_to_md.core:start_cli',
                                      'npdoc-to_md=npdoc_to_md.core:start_cli',
                                      'npdoc_to-md=npdoc_to_md.core:start_cli']},
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=requirements,
    classifiers=["Development Status :: 5 - Production/Stable",
                 "Programming Language :: Python :: 3",
                 "Programming Language :: Python :: 3.6",
                 "Programming Language :: Python :: 3.7",
                 "Programming Language :: Python :: 3.8",
                 "Programming Language :: Python :: 3.9",
                 "Programming Language :: Python :: 3.10",
                 "License :: Public Domain",
                 "Intended Audience :: Developers",
                 "Operating System :: OS Independent"])
