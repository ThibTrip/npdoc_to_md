import setuptools
import os

here = os.path.abspath(os.path.dirname(__file__))

description = 'Easy conversion of Python docstrings in numpy style to markdown! Includes a Markdown renderer.'

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
    version="1.1",
    license = 'The Unlicense',
    author="Thibault Bétrémieux",
    author_email="thibault.betremieux@gmail.com",
    url = 'https://github.com/ThibTrip/npdoc_to_md',
    download_url = 'https://github.com/ThibTrip/npdoc_to_md/archive/v1.1.tar.gz',
    keywords = ['numpydoc','documentation', 'docstrings', 'python'],
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires= requirements,
    classifiers=["Development Status :: 5 - Production/Stable",
                 "Programming Language :: Python :: 3",
                 "Programming Language :: Python :: 3.6",
                 "Programming Language :: Python :: 3.7",
                 "Programming Language :: Python :: 3.8",
                 "License :: Public Domain",
                 "Intended Audience :: Developers",
                 "Operating System :: OS Independent"])
