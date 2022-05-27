# +
"""
Contains all objects that will be directly exposed to the users of the library
e.g. `render_obj_docstring`
"""
from functools import wraps
import logging
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional, Union

# local imports
from npdoc_to_md.helpers import FileOperations, Patterns
from npdoc_to_md.logger import log
from npdoc_to_md.parsers import parse_and_render
from npdoc_to_md.placeholder import Config, Placeholder


# -
# # Local helpers

# +
@dataclass(frozen=True)
class RenderedFile:
    """
    Represents a template file that has been converted by the npdoc_to_md library.

    The attributes listed below are also the parameters for making an instance.
    All parameters are mandatory.

    Note that for the attributes "_" and "-" are interchangeable (e.g. "original_text"
    and "original-text" will both work). This was made to simplify the CLI usage.

    Attributes
    ----------
    source
        Filepath to the template
    destination
        Filepath to the rendered template or None if the user did
        not wish to save the result to a file
    original_text
        Text of the template file
    rendered_text
        Text obtained after rendering the template file (after a function
        from npdoc_to_md was used)
    """
    source:str
    destination:Union[str, None]
    original_text:str
    rendered_text:str

    def __getattr__(self, attr:str):
        """
        We overwrite __getattr__ to allow aliases such as "original-text" for the CLI.
        """
        return self.__getattribute__(attr.replace('-', '_'))

    def __repr__(self):
        return (f'source: {self.source}\n'
                f'destination: {self.destination}\n'
                f'original_text: see attribute "original_text" (hidden to avoid cluttering the output)\n'
                f'rendered_text:\n{self.rendered_text}')


@dataclass(frozen=True)
class RenderedFileCLI(RenderedFile):
    """
    Same as class npdoc_to_md.RenderedFile (see its docstring)
    where the string form (str(instance)) has been changed for the CLI.
    Indeed, the string form will give the same result as the repr
    (repr(instance)).
    """

    def __str__(self):
        return super().__repr__()

    @classmethod
    def _from_rendered_file(cls, obj:RenderedFile):
        assert isinstance(obj, RenderedFile)
        return cls(**asdict(obj))


class RenderedFilesCLI(list):
    """
    Container for multiple instances of RenderedFileCLI.
    Behaves like a list but the string form (str(instance)) has been
    changed for the CLI.

    Examples
    --------
    >>> data = [RenderedFileCLI(source='test.md', destination='test.md', original_text='foo', rendered_text='foo')]
    >>> rfc = RenderedFilesCLI(data)
    >>> rfc
    [RenderedFileCLI(source='test.md', destination='test.md', original_text='foo', rendered_text='foo')]
    >>> len(rfc)
    1
    >>> rfc[0]
    RenderedFileCLI(source='test.md', destination='test.md', original_text='foo', rendered_text='foo')
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for obj in self:
            assert isinstance(obj, RenderedFileCLI)

    def __str__(self):  # pragma: no cover
        strings = []
        nb_files = len(self)
        for ix, f in enumerate(self):
            # make a separator so we can distinguish files more easely
            begin = '\n\n' if ix != 0 else ''
            strings.append(f'{begin}{"$"*50} FILE {ix + 1}/{nb_files} {"$"*50}\n')
            strings.append(f.__str__())
        return ''.join(strings)


# -

# # Render using Python objects

# IMPORTANT! further down the line (in other modules) `obj` will be referred to as `obj_namespace`
# and `obj` will be the actual Python object at given importable path
def render_obj_docstring(obj:str,
                         alias:Optional[str]=Config.get_default('alias'),
                         examples_md_lang:str=Config.get_default('examples_md_lang'),
                         remove_doctest_blanklines:bool=Config.get_default('remove_doctest_blanklines'),
                         remove_doctest_skip:bool=Config.get_default('remove_doctest_skip'),
                         md_section_level:int=Config.get_default('md_section_level'),
                         ignore_custom_section_warning:bool=Config.get_default('ignore_custom_section_warning'),
                         members:Optional[List[str]]=None) -> str:
    """
    Converts the docstring of an object (e.g. function, class, method, module, ...)
    to a pretty markdown string.

    It uses the same parameters as the ones for placeholders described
    in the wiki of the library.
    See wiki folder at the root of the repo or https://github.com/ThibTrip/npdoc_to_md/wiki

    CLI Examples
    ------------
    Note that "-" and "_" are interchangeable

    ```
    $ npdoc-to-md render-obj-docstring -obj "datetime.datetime" --alias "datetime" --examples-md-lang "raw" --md-section-level 3 --remove-doctest-skip --remove-doctest-blanklines

    $ npdoc-to-md render-obj-docstring -obj "pandas" --examples-md-lang "raw" --members "['DataFrame']"

    $ npdoc-to-md render-obj-docstring -obj "pandas.DataFrame" --alias "pd.DataFrame" --examples-md-lang "raw" --members "['public$', '+__dict__', '-to_dict']"
    ```

    Examples
    --------
    >>> from npdoc_to_md import render_obj_docstring
    >>>
    >>> md = render_obj_docstring(obj="npdoc_to_md.testing.now_utc",
    ...                           alias="now_utc",
    ...                           examples_md_lang='raw',
    ...                           remove_doctest_skip=True,
    ...                           remove_doctest_blanklines=True,
    ...                           md_section_level=3)
    """
    if not isinstance(obj, str):
        raise TypeError('Expected parameter `obj` to be a string of an importable python object '
                        f'e.g. "pandas.DataFrame", "datetime.datetime", ... . Got type {type(obj)} instead')

    config = Config(alias=alias,
                    examples_md_lang=examples_md_lang,
                    remove_doctest_blanklines=remove_doctest_blanklines,
                    remove_doctest_skip=remove_doctest_skip,
                    md_section_level=md_section_level,
                    ignore_custom_section_warning=ignore_custom_section_warning,
                    members=[] if members is None else members)
    return parse_and_render(obj_namespace=obj, config=config)


# # Render using text 

# ## Helpers to render a single placeholder

# +
def _render_placeholder(placeholder:Placeholder) -> str:
    r"""
    Uses instructions in given placeholder (syntax given by library)
    to find a Python object and render its docstring in Markdown.

    Examples
    --------
    >>> from npdoc_to_md.placeholder import Placeholder
    >>>
    >>> p = Placeholder('{{"obj":"npdoc_to_md.testing.now_utc", "alias":"now_utc", "examples_md_lang":"raw"}}')
    >>> md = _render_placeholder(placeholder=p)
    """
    config:Config = placeholder.config
    rendered = render_obj_docstring(obj=placeholder.obj_namespace,
                                    alias=config.alias,
                                    examples_md_lang=config.examples_md_lang,
                                    remove_doctest_blanklines=config.remove_doctest_blanklines,
                                    remove_doctest_skip=config.remove_doctest_skip,
                                    md_section_level=config.md_section_level,
                                    ignore_custom_section_warning=config.ignore_custom_section_warning,
                                    members=config.members)
    return rendered


def _render_placeholder_no_err(placeholder:Placeholder) -> str:
    """
    Similar to `_render_placeholder` but logs errors instead of raising
    them.

    Examples
    --------
    >>> from npdoc_to_md.placeholder import Placeholder
    >>>
    >>> # this is obviously not going to work (no module named monkey)
    >>> # but it will not raise any exception
    >>> p = Placeholder('{{"obj":"monkey"}}')
    >>> md = _render_placeholder_no_err(placeholder=p)
    >>>
    >>> # the placeholder is returned as is, no conversion was done
    >>> print(md)
    {{"obj":"monkey"}}
    """
    try:
        return _render_placeholder(placeholder=placeholder)
    except Exception:
        log(f'An exception occured when rendering this placeholder: {placeholder}',
            level=logging.ERROR, exc_info=True)
        return placeholder.line


# -

# ## Function to render from text

def render_string(string:str, ignore_errors:bool=False) -> str:
    r'''
    Returns a markdown string where placeholders defined in this library have
    been replaced with the corresponding docstrings rendered in Markdown.

    See wiki folder at the root of the repo or https://github.com/ThibTrip/npdoc_to_md/wiki
    and the examples for the placeholders syntax.

    Parameters
    ----------
    string
        String with markdown syntax (we will split it in lines)
        containing (or not) placeholders defined in this library
    ignore_errors
        If True only logs errors relative to converting placeholders
        in the string otherwise raises such errors.
        Also, placeholders that failed to convert will
        be unchanged in the resulting text

        Note that any string that begings with "{{" and ends with "}}" on the
        same line is interpreted as a placeholder by the library.

    CLI Examples
    ------------
    Note that "-" and "_" are interchangeable.

    While I do make this method available for the CLI, if you are going to do similar
    things as the examples below, I would suggest looking at the other functions of
    the library for generating documentation. Indeed, unless you are in Bash and can use a multiline string,
    the escaping is tricky as you can see below.

    IMPORTANT: do not put spaces in the placeholders (e.g. between commas) otherwise the parsing would fail (because
    space is a character used to separate arguments)

    Bash example:

    ```
    $ STRING='"{{\"obj\":\"npdoc_to_md.testing.DocumentedClassExample\",\"remove_doctest_blanklines\":true,\"remove_doctest_skip\":true,\"examples_md_lang\":\"raw\",\"members\":[\"public$\"]}}"'
    $ npdoc-to-md render-string -string "$STRING"
    ```

    Command Prompt example (Windows):

    ```
    $ set STRING='"{{\"obj\":\"npdoc_to_md.testing.DocumentedClassExample\",\"remove_doctest_blanklines\":true,\"remove_doctest_skip\":true,\"examples_md_lang\":\"raw\",\"members\":[\"public$\"]}}"'
    $ npdoc-to-md render-string -string %STRING%
    ```

    Bash example (multiline):

    ```
    $ STRING='Demo:
    > {{"obj":"npdoc_to_md.testing.DocumentedClassExample", "remove_doctest_blanklines":true, "md_section_level":3, "members":["public$"]}}'
    $ npdoc-to-md render-string -string "$STRING"
    ```

    Examples
    --------
    >>> from npdoc_to_md import render_string
    >>>
    >>> text = """
    ... Here is a demo of npdoc_to_md.render_string. The placeholder
    ... below will be converted to a docstring in markdown:
    ...
    ... ---
    ...
    ... {{"obj":"npdoc_to_md.testing.now_utc", "alias":"now_utc"}}
    ... """
    >>> md = render_string(string=text)

    >>> # demonstrating "ignore_errors": this raises no error even though we are referring to a non existent object
    >>> md = render_string(string='{{"obj":"some_object_that_does_not_exist"}}', ignore_errors=True)
    '''
    if ignore_errors:
        render_placeholder_method = _render_placeholder_no_err
        search_placeholder_method = Placeholder.search_no_err
    else:
        render_placeholder_method = _render_placeholder
        search_placeholder_method = Placeholder.search

    new_lines:List[str] = []
    for line in string.splitlines():
        placeholder:Union[Placeholder, None] = search_placeholder_method(line)
        if placeholder is not None:
            rendered = render_placeholder_method(placeholder=placeholder)
            new_lines.append(rendered)
        else:
            new_lines.append(line)
    return '\n'.join(new_lines)


# # Render using file

def render_file(source:str, destination:Optional[str]=None,
                ignore_errors:bool=False) -> Union[RenderedFile, RenderedFileCLI]:
    """
    Reads markdown file at path `source` and replaces placeholders defined in this library
    with the corresponding docstrings. It then returns the "converted" text.

    If a `destination` is given we save the converted text at this path.

    See wiki folder at the root of the repo or https://github.com/ThibTrip/npdoc_to_md/wiki
    for the placeholders syntax.

    Parameters
    ----------
    source
        Path to the markdown file
    destination
        If None only returns a converted markdown string.
        Otherwise it also creates or overwrites the file
        at this path with the converted markdown string.
    ignore_errors
        Same logic as in function `render_string` (see its docstring)

    CLI Examples
    ------------
    Note that "-" and "_" are interchangeable

    ```
    $ npdoc-to-md render-file -source "./docs/Render file.npmd" --destination "./docs/Render file.md"
    ```

    Since we are using python-fire for the CLI it is possible to access attributes
    of the class (RenderedFile) instance that is returned. In the example below
    we are acccessing the attribute `rendered_text`:

    ```
    $ npdoc-to-md render-file -source "./docs/Render file.npmd" --destination "./docs/Render file.md" - rendered-text
    ```

    See also the python-fire guide: https://github.com/google/python-fire/blob/master/docs/guide.md

    Returns
    -------
    npdoc_to_md.RenderedFile | npdoc_to_md.RenderedFileCLI
        Returns RenderedFile object if using this function in Python.
        Returns RenderedFileCLI if using this function in CLI.
        See docstring of these objects.

    Examples
    --------
    >>> from npdoc_to_md import render_file
    >>>
    >>> source = "./README.md"
    >>> destination = "./README_converted.md"
    >>> rendered_file = render_file(source=source, destination=destination) # doctest: +SKIP
    """
    # read contents
    log(f'Reading file contents at path {source}')
    with open(source, mode='r', encoding='utf-8', newline='\n') as fh:
        original_text = fh.read()
    # render
    log('Rendering file contents')
    rendered_text = render_string(string=original_text, ignore_errors=ignore_errors)

    # save
    if destination is not None:
        log(f'Saving rendered contents to path {destination}')
        with open(destination, mode='w', encoding='utf-8', newline='\n') as fh:
            fh.write(rendered_text)
    return RenderedFile(source=source, destination=destination,
                        original_text=original_text, rendered_text=rendered_text)


# # Render using folder

def render_folder(source:str,
                  destination:Optional[str]=None,
                  recursive:bool=False,
                  ignore_errors:bool=False,
                  pattern:Optional[str]=None,
                  case_sensitive:bool=False) -> Union[List[RenderedFile], RenderedFilesCLI]:
    r"""
    Reads all markdown files in the folder at path `source`
    and for each markdown file, replaces placeholders defined in this library
    with the corresponding docstrings.

    If a `destination` folder is given we also save converted files there using
    the same folder structure (case of `recursive=True`) and also the same
    file names, except the extensions that always get converted to ".md"
    (unless they already matched ".md" case insensitive) e.g.:
    * `some_lib/docs_templates/Home.npmd` -> `some_lib/docs/Home.md`
    * `some_lib/docs_templates/Logging.MD` -> `some_lib/docs/Logging.MD`
    * `some_lib/docs_templates/cool_subpackage/Home.npmd` -> `some_lib/docs/cool_subpackage/Home.md`

    See wiki folder at the root of the repo or https://github.com/ThibTrip/npdoc_to_md/wiki
    for the placeholders syntax.

    Parameters
    ----------
    source
        Path to the folder containing markdown files
    destination
        If None no file operations is done but you still get the result
        of the rendering (see sections Examples | CLI Examples and Returns)
    recursive
        If False only looks for markdown files directly in folder `source`
        otherwise also looks inside subfolders
    ignore_errors
        Same logic as in function `render_string` (see its docstring)
    pattern
        Regex pattern for matching file names in folder `source`
        e.g. "(\.md|\.txt)$" (file names with the extension ".md"
        or ".txt")

        By default we use a regex pattern matching "md" and "npmd"
        extensions. See attributes `template_files` and `template_files_insensitive`
        of class `npdoc_to_md.helpers.Patterns`
    case_sensitive
        Whether the `pattern` is case sensitive. By default this is False (`pattern` is
        case insensitive)

    CLI Examples
    ------------
    Note that "-" and "_" are interchangeable

    ```
    $ npdoc-to-md render-folder -source "./docs" --destination "./docs" --ignore-errors --recursive
    ```

    Since we are using python-fire for the CLI it is possible to work with the returned object (a list
    of RenderedFileCLI instances). In the example below we are acccessing the attribute `rendered_text`
    of the first item:

    ```
    $ npdoc-to-md render-folder -source "./docs" --destination "./docs" --ignore-errors --recursive - 0 - rendered_text
    ```

    See also the python-fire guide: https://github.com/google/python-fire/blob/master/docs/guide.md

    Returns
    -------
    list[npdoc_to_md.RenderedFile] | RenderedFilesCLI
        Returns list[RenderedFile] if using this function in Python.
        Returns RenderedFilesCLI if using this function in the CLI.

        See docstring of these objects.

    Examples
    --------
    >>> from npdoc_to_md import render_folder
    >>>
    >>> source = "./docs_templates"
    >>> destination = "./docs"
    >>> rendered_files = render_folder(source=source, destination=destination) # doctest: +SKIP
    """
    # get pattern object for extensions
    if pattern is None:
        pattern:re.Pattern = Patterns.template_files if case_sensitive else Patterns.template_files_insensitive
    else:
        flags = re.UNICODE if case_sensitive else re.IGNORECASE | re.UNICODE
        pattern = re.compile(pattern, flags=flags)

    # get markdown files in folder
    filepaths = FileOperations.list_files(folder=source, pattern=pattern, recursive=recursive)
    nb_files = len(filepaths)

    # render markdown files
    rendered_files = []
    log(f'{"#"*10} Processing folder "{source}" {"#"*10}')
    for ix, filepath in enumerate(filepaths):
        log(f'{"-"*10} Processing path {ix+1}/{nb_files} {"-"*10}')
        if destination is not None:
            destination_path = FileOperations.switch_folder(source_folder=source,
                                                            destination_folder=destination,
                                                            filepath=filepath)
            # replace extension to Markdown (case of template or otherwise)
            not_md = not destination_path.lower().strip().endswith('.md')
            if not_md:
                destination_path = str(Path(destination_path).with_suffix('.md'))
        else:
            destination_path = None
        rendered_file = render_file(source=filepath, destination=destination_path, ignore_errors=ignore_errors)
        rendered_files.append(rendered_file)
    return rendered_files


# # Start CLI

def start_cli() -> None:
    """
    Starts the Command Line Interface for the library.
    Is also the entry point in the file `setup.py`
    """
    try:
        import fire
    except ModuleNotFoundError as e:
        raise ModuleNotFoundError('Please install optional dependency "fire" (pip install fire) '
                                  'if you want to use the CLI') from e

    # change return types for render_file and render_folder
    def rendered_files_to_rendered_files_cli(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if isinstance(result, RenderedFile):
                return RenderedFileCLI._from_rendered_file(obj=result)
            elif isinstance(result, list):
                assert all(isinstance(f, RenderedFile) for f in result)
                return RenderedFilesCLI(RenderedFileCLI._from_rendered_file(obj=f) for f in result)
            else:
                raise TypeError(f'Unexpected return type from function {func.__name__}: {type(result)}')
        return wrapper

    # cli mapping (which subcommand executes which function)
    cli_mapping = {'render-obj-docstring':render_obj_docstring,
                   'render-string':render_string,
                   'render-file':rendered_files_to_rendered_files_cli(render_file),
                   'render-folder':rendered_files_to_rendered_files_cli(render_folder)}

    # make it possible to use hyphens or underscore for subcommand
    # (I prefer transforming the arg to adding subcommands in the `cli_mapping`
    # because this would clutter the help)
    def hyphenize_subcommand():
        # check if argument was passed
        subcommand_ix = 1
        arg_passed = len(sys.argv) >= subcommand_ix + 1
        if not arg_passed:  # pragma: no cover
            return
        # check if argument has an underscore
        arg = sys.argv[subcommand_ix]
        if '_' not in arg:
            return
        # change the argument and check if it corresponds to any subcommand
        aliased = arg.replace('_', '-')
        if aliased in cli_mapping:
            log(f'Transformed subcommand: {arg} -> {aliased}', level=logging.DEBUG)
            sys.argv[subcommand_ix] = aliased

    hyphenize_subcommand()

    # fire CLI
    fire.Fire(cli_mapping)
