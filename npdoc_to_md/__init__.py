"""
Automatic documentation tool using Markdown and Python docstrings written in numpydoc style

See documentation in the wiki folder at the root of the repo or go to https://github.com/ThibTrip/npdoc_to_md/wiki
"""
from npdoc_to_md._version import __version__
from npdoc_to_md.core import RenderedFile, RenderedFileCLI, RenderedFilesCLI, render_obj_docstring, render_string, render_file, render_folder