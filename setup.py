import setuptools
import os

here = os.path.abspath(os.path.dirname(__file__))

DESCRIPTION = 'Easy conversion of Python docstrings in numpy style to markdown! Includes a Markdown renderer.'

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION


with open(os.path.join(here, "requirements.txt"),"r") as f:
    requirements = [line.strip() for line in f.readlines()]

setuptools.setup(
    name="npdoc_to_md",
    version="0.1",
    author="Thibault Bétrémieux",
    author_email="thibault.betremieux@port-neo.com",
    description= DESCRIPTION,
    long_description = long_description,
    long_description_content_type = "text/markdown",
    packages = setuptools.find_packages(),
    include_package_data=True,
    zip_safe = False,
    install_requires= requirements,
    classifiers=["Programming Language :: Python :: 3",
                 "License :: None",
                 "Operating System :: OS Independent"])
