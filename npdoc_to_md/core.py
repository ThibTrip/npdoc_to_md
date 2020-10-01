# +
import inspect
import logging
import re
import json
import pathlib
from pydoc import locate
from numpydoc.docscrape import (NumpyDocString,
                                FunctionDoc,
                                ClassDoc)
from npdoc_to_md.helpers import numpydoc_section_to_md_lines

# regex to remove self argument in methods or cls in classmethods
RE_SELF_ARG = re.compile('(?<=\()(self|cls) *\,* *')

# configure logger
logging_format = ('%(asctime)s | %(levelname)s     '
                  '| npdoc_to_md     | %(module)s:%(funcName)s:%(lineno)s '
                  '- %(message)s')
logging.basicConfig(format=logging_format, datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger('pangres')
logger.setLevel(logging.INFO)


# -

# # Parse from object

def render_md_from_obj_docstring(obj, obj_namespace, examples_md_flavor='python', remove_doctest_blanklines=True):
    """
    Converts the docstring of an object (e.g. function, class, method)
    to a pretty markdown string.

    **IMPORTANT**

    1. The docstring must be a valid pandas/numpy style docstring! See the following resources:
       * https://pandas.pydata.org/pandas-docs/stable/development/contributing_docstring.html#docstring
       * https://numpydoc.readthedocs.io/en/latest/format.html
    2. Before any example in the docstring you can define the markdown flavor/language for its
       output like this: {{LANGUAGE}} e.g. {{markdown}}, {{python}} or {{raw}} for no language
       which creates a raw markdown code block.
       When you do this, this overrides the parameter examples_md_flavor (see Parameters).

    Notes
    -----
    The parameter obj_namespace (e.g. pandas.DataFrame) would be optional
    if I was able to retrieve it automatically from the parameter obj but
    I am not sure this is always possible.

    Parameters
    ----------
    obj : class, function, method
    obj_namespace : str
        Function namespace that should be used for the markdown.
        You can also use your own aliases. For instance
        pd.DataFrame instead of pandas.DataFrame.
    examples_md_flavor : str
        In which language/flavor to render example outputs.
        See https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet#code-and-syntax-highlighting
        By default example outputs are encapsulated by \```python\```
        to create a markdown Python code block. You can use any flavor
        you please or the special flag "raw" which will be a code block
        without flavor. If you choose "markdown" there is no encapsulation.
    remove_doctest_blanklines : bool, default True
            If True, replaces "<BLANKLINE>" used for doctest with an empty string.
            See https://docs.python.org/3.8/library/doctest.html#how-are-docstring-examples-recognized

    Examples
    --------
    >>> from pandas import Series
    >>> from npdoc_to_md import render_md_from_obj_docstring
    >>> 
    >>> md = render_md_from_obj_docstring(obj=Series, obj_namespace="pd.Series")
    """
    # escape "_" (use HTML code as in some situations \_ may be displayed instead of _)
    obj_namespace = obj_namespace.replace('_', '&#95;')
    # don't get the signature using numpydoc but instead use inspect and modify
    # the object name (this is useful if we use an alias e.g.
    # pd.DataFrame instead of pandas.DataFrame)
    obj_sig = str(inspect.signature(obj))
    # remove self argument
    obj_sig = RE_SELF_ARG.sub('', obj_sig)
    obj_sig = f"""**<span style="color:purple">{obj_namespace}</span>_{obj_sig}_**\n\n"""
    # parse the object docstring using classes from numpydoc.docscrape
    if inspect.isclass(obj):
        doc = ClassDoc(obj)
    elif inspect.isfunction(obj) or inspect.ismethod(obj):
        doc = FunctionDoc(obj)
    # prepare all the lines
    lines = [obj_sig]
    for section_name in doc.sections:
        # we already dealt with "Signature" and idk what "index" is
        if section_name in ('Signature', 'index'):
            continue
        # bug where a section does not exists and it is still parsed by numpydoc
        # for instance this happened with the section Attributes of pd.DataFrame
        header_exists = any(l.strip().startswith(section_name)
                            for l in obj.__doc__.splitlines())
        if not header_exists and section_name not in ('Summary', 'Extended Summary'):
            continue
        converted = numpydoc_section_to_md_lines(doc,
                                                 section_name=section_name,
                                                 examples_md_flavor=examples_md_flavor,
                                                 remove_doctest_blanklines=remove_doctest_blanklines)
        lines.extend(converted)
    # assemble the lines
    md = '\n'.join(lines).strip()
    return md


# # Parse from placeholder
#
# e.g. <code>{{"obj":"npdoc_to_md.testing.example_func"}}</code>

def _render_placeholder_string(placeholder_string):
    """
    Converts the docstring of a Python function, class or method
    defined in a placeholder (see placeholder_string in Parameters)
    to a pretty markdown string.

    **IMPORTANT**

    1. The docstring must be a valid pandas/numpy style docstring! See the following resources:
       * https://pandas.pydata.org/pandas-docs/stable/development/contributing_docstring.html#docstring
       * https://numpydoc.readthedocs.io/en/latest/format.html
    2. Before any example in the docstring you can define the markdown flavor/language for its
       output like this: {{LANGUAGE}} e.g. {{markdown}}, {{python}} or {{raw}} for no language
       which create a raw markdown code block.
       When you do this, this overrides the key "ex_md_flavor" in the placeholder (see Parameters).

    Parameters
    ----------
    placeholder_string : str
        JSON dictionnary decorated by {} (see Examples). Keys:
        * "obj": name of an importable Python class, function or method
        * _(optional)_ "alias": namespace to use for the markdown render
            (e.g. pd.DataFrame instead of pandas.DataFrame). If this is not
            provided then the namespace is taken from the key "obj".
        * _(optional)_ "ex_md_flavor": In which language/flavor to render example outputs.
            See https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet#code-and-syntax-highlighting
            If not provided outputs are encapsulated by \```python\```
            to create a markdown Python code block. You can use any flavor
            you please or the special flag "raw" which will be a code block
            without flavor. If you choose "markdown" there is no encapsulation.
        * _(optional)_ "remove_doctest_blanklines": If True (default), replaces "<BLANKLINE>"
            used for doctest with an empty string.
            See https://docs.python.org/3.8/library/doctest.html#how-are-docstring-examples-recognized

    Examples
    --------
    >>> from npdoc_to_md.core import _render_placeholder_string
    >>> 
    >>> md = _render_placeholder_string('{{"obj":"pandas.DataFrame", "alias":"pd.DataFrame", "ex_md_flavor":"raw"}}')
    """
    # remove one pair of brackets so instead of {{data}} we have {data}
    # and it can be read as JSON
    parsed = json.loads(placeholder_string[1:-1])
    # check keys
    allowed_keys = {'alias', 'obj', 'ex_md_flavor', 'remove_doctest_blanklines'}
    not_allowed_keys = set(parsed.keys()) - allowed_keys
    if not_allowed_keys:
        raise ValueError((f'Invalid keys used for placeholder string: {not_allowed_keys}\n'
                          f'Valid keys are: {allowed_keys}\n'
                          f'Placeholder string that caused error was "{placeholder_string}"'))
    # get the object namespace
    obj_namespace = parsed['alias'] if 'alias' in parsed else parsed['obj']
    # import object or method
    obj = locate(parsed['obj'])
    # search for examples md flavor
    examples_md_flavor = parsed.get('ex_md_flavor','python')
    # check if the user wants doctest blanklines removed
    ## for JSON the user should write "true" instead of "True" but in case he forgets we can convert that
    remove_doctest_blanklines = parsed.get('remove_doctest_blanklines', True)
    if isinstance(remove_doctest_blanklines, str):
        if remove_doctest_blanklines.lower() == 'true':
            remove_doctest_blanklines = True
        elif remove_doctest_blanklines.lower() == 'false':
            remove_doctest_blanklines = False
    ## at this point remove_doctest_blanklines must be a bool
    if remove_doctest_blanklines not in (True, False):
        raise ValueError('Argument remove_doctest_blanklines must be a boolean!')

    # convert to md
    rendered = render_md_from_obj_docstring(obj, obj_namespace, examples_md_flavor=examples_md_flavor,
                                            remove_doctest_blanklines=remove_doctest_blanklines)
    return rendered


# # Parse from markown file

def render_md_file(source, destination=None, allow_same_path=False):
    """
    Renders a markdown file containing (or not) placeholders - see **docstring of
    npdoc_to_md.render_placeholder_string** !! - to automatically fetch and convert
    Python docstrings to pretty markdown.

    **IMPORTANT**

    1. The docstring must be a valid pandas/numpy style docstring! See the following resources:
       * https://pandas.pydata.org/pandas-docs/stable/development/contributing_docstring.html#docstring
       * https://numpydoc.readthedocs.io/en/latest/format.html
    2. Before any example in the docstring you can define the markdown flavor/language for its
       output like this: {{LANGUAGE}} e.g. {{markdown}}, {{python}} or {{raw}} for no language
       which create a raw markdown code block.
       When you do this, this overrides the key "ex_md_flavor" in placeholders (see section Parameters
       in the docstring of the function npdoc_to_md.render_placeholder_string).
    3. A placeholder must be at the beginning of a line and this line cannot contain anything else!
        * Bad example: <code>* {{"obj":"somefunc"}} <- this is a cool function</code>
        * Good example: <code>{{"obj":"somefunc"}}</code>
    
    Parameters
    ----------
    source : str
        Path to the markdown file
    destination : str or None, default None
        If None returns a rendered markdown string.
        Otherwise creates or overwrites a rendered file.
        destination cannot be equal to source!
    allow_same_path : bool, default False
        If :source: is the same as :destination: and
        allow_same_path is False then an error is raised.
        In any other case the value of this parameter
        does not change the behavior of the function.

    Raises
    ------
    ValueError
        If destination is the same as source and allow_same_path is False
    
    Examples
    --------
    >>> from npdoc_to_md import render_md_file
    >>> 
    >>> # set source and destination
    >>> source = "./README_UNRENDERED.md"
    >>> destination = "./README.md"
    >>> 
    >>> md = render_md_file(source, destination) # doctest: +SKIP
    """
    with open(source, mode='r', encoding='utf-8') as fh:
        content = fh.read()
    splitted = content.splitlines()
    rendered_lines = []
    
    for ix, line in enumerate(splitted):
        line = line.rstrip('\n')
        # find strings like {{my_class,my_method,my_alias}}
        if line.startswith('{{') and line.endswith('}}'):
            try:
                md = _render_placeholder_string(line)
            except Exception as e:
                logger.error(f'Could not render line {ix}: "{line}" in file "{source}"', exc_info=e)
                # add unrendered line
                rendered_lines.append(line)
                continue
            rendered_lines.append(md)
        else:
            rendered_lines.append(line)
    new_content = '\n'.join(rendered_lines)
    if destination is not None:
        if (pathlib.Path(source) == pathlib.Path(destination)) and not allow_same_path:
            raise ValueError(('source cannot be the same as destination! '
                              'This is to avoid accidental overwriting of your docs.'))
        with open(destination, mode='w', encoding='utf-8') as fh:
            fh.write(new_content)
    return new_content
