# +
"""
Contains parsers for every sections listed by numpydoc and also a main
function `parse_and_render` that uses these parsers to convert docstrings
to markdown.

See sections in https://numpydoc.readthedocs.io/en/latest/format.html
"""
import dataclasses
import inspect
import pydoc
from abc import ABC, abstractmethod
from dataclasses import dataclass, field as dataclassfield
from numpydoc.docscrape import Parameter
from typing import Any, ClassVar, List, Tuple

# local imports
from npdoc_to_md.exceptions import (MembersConflictsException,
                                    InvalidMembersFlagException,
                                    NonExistentMemberException,
                                    NonExistentObjectException,
                                    SignatureNotFoundException)
from npdoc_to_md.helpers import Patterns, unique
from npdoc_to_md.examples_labeller import (ExampleBlock, ExamplesLabeller,
                                           ExampleLine, ExampleLineType)
from npdoc_to_md.logger import log
from npdoc_to_md.config import MemberFlag, Config, SpecialExampleOutputLanguages
from npdoc_to_md.sections import SectionsFinder


# -

# # Helpers

# ## Generic helpers

# +
class MdEscaper:
    r"""
    Escapes problematic characters for strings that are supposed
    to be rendered "as-is" and not in Markdown e.g. a function
    signature.

    Examples
    --------
    >>> MdEscaper.escape('foo(self, *some_args)')
    'foo(self, \\*some\\_args)'
    """
    translator = {ord(c):f'\\{c}' for c in ('_', '*')}

    def escape(s:str) -> str:
        return s.translate(MdEscaper.translator)


def param_description_lines_to_md_lines(desc_lines:List[str]) -> List[str]:
    """
    Formats the descriptions found below parameter names (numpydoc sections "Parameters",
    "Other Parameters", "Returns", "Yield", ...) or function names (numpydoc sections
    "See Also", ...).

    Notes
    -----
    After some trials I decided to format these lines by only adding 2 leading spaces because:
    * 1 leading space: it is ignored
    * 2 to 5: makes a bullet level indent (for all values so might as well use 2 spaces)
    * 6+ spaces: always makes a code block which breaks markdown formatting such as bullets :(

    Note that using &nbsp; and such is bad idea because we'd have to understand when markdown
    needs a new line or not (with tables and such it gets complicated quickly...)
    """
    return [(' ' * 2) + line if line.strip() else line for line in desc_lines]


# -

# ## Parser for the members of a Python object

@dataclass(frozen=True)
class MembersParser:
    """
    Parses the values in the field "members" of the placeholders
    as described in the wiki.
    See also Examples which are quite self-explanatory.

    Parameters
    ----------
    obj
        A Python object
    members
        Raw values of the field "members" in a placeholder

    Attributes
    ----------
    parsed_members
        Result obtained after parsing `members`: all the
        members that we will have to fetch the docstring
        from

    Examples
    --------
    >>> from npdoc_to_md.config import MemberFlag
    >>>
    >>> class Foo():
    ...     def __init__(self): pass
    ...     def _private_method1(self): pass
    ...     def _private_method2(self): pass
    ...     def __dunder_method1__(self): pass
    ...     def __dunder_method2__(self): pass
    ...     def public_method1(self): pass
    ...     def public_method2(self): pass
    >>>
    >>> public = MemberFlag.PUBLIC.value
    >>> private = MemberFlag.PRIVATE.value
    >>> dunder = MemberFlag.DUNDER.value
    >>>
    >>> MembersParser(obj=Foo, members=[public, '-public_method1', private]).parsed_members
    ('public_method2', '_private_method1', '_private_method2')

    >>> MembersParser(obj=Foo, members=['+public_method1', 'public_method2', dunder]).parsed_members[0:5]
    ('public_method1', 'public_method2', '__class__', '__delattr__', '__dict__')
    """
    obj:Any
    members:List[str]
    members_parsed:Tuple[str] = dataclassfield(init=False)
    allowed_flags:ClassVar[Tuple[str]] = tuple(f.value for f in MemberFlag)
    _all_members:List[str] = dataclassfield(init=False, repr=False)

    def _parse_flag(self, flag:str) -> List[str]:
        """
        Helper for __post_init__
        """
        if flag == MemberFlag.DUNDER.value:
            return [v for v in self._all_members if v.startswith('__')]
        elif flag == MemberFlag.PRIVATE.value:
            return [v for v in self._all_members if v.startswith('_') and not v.startswith('__')]
        elif flag == MemberFlag.PUBLIC.value:
            return [v for v in self._all_members if not v.startswith('_')]
        else:
            raise InvalidMembersFlagException('Flags for documenting members must be one of: '
                                              f'{self.allowed_flags}. Got: "{flag}"')

    def _parse_member_to_include(self, value:str) -> str:
        """
        Helper for __post_init__
        """
        # handle case of included with "+" syntax
        value = value[1:] if value.startswith('+') else value
        if value not in self._all_members:
            raise NonExistentMemberException(f'Object {self.obj} does not have any attribute: "{value}"')
        return value

    def __post_init__(self):
        # clean members listed by the users
        members = [m.strip() for m in self.members]
        if any(m == '' for m in members):
            raise ValueError('An empty string is not a valid member name for a Python object. '
                             f'Value of parameter `members` was: {members}')
        object.__setattr__(self, 'members', members)
        object.__setattr__(self, '_all_members', dir(self.obj))  # this is for avoiding many calls to `dir`

        candidates = []
        exclusions = []
        inclusions = []
        for m in members:
            if m in self.allowed_flags:
                candidates.extend(self._parse_flag(m))
            elif m.startswith('-'):
                exclusions.append(m[1:])
            else:
                # case "+member" or just "member"
                parsed = self._parse_member_to_include(m)
                candidates.append(parsed)
                inclusions.append(parsed)

        # case when we have members both excluded and included
        conflicts = set(exclusions) & set(inclusions)
        if conflicts:
            raise MembersConflictsException(f'The following members in object {self.obj} are set to be '
                                            f'included AND excluded: {conflicts}')

        # finalize parsing
        parsed_members = [c for c in unique(candidates) if c not in exclusions]
        object.__setattr__(self, 'parsed_members', tuple(parsed_members))


# ## Base parsers for numpy sections

# +
@dataclass(frozen=True)
class DocParser(ABC):
    '''
    Abstract class for taking information from a numpydoc section (numpydoc
    always give back a list of items for each section) and converting it to
    Markdown lines (with method `to_md_lines`)

    Parameters
    ----------
    lines
        list of str, numpydoc.docscrape.Parameter, ...
        What's inside the list depends on the numpydoc section
        but the types are never mixed
    config
        "Global" configuration - parameters that will be used
        in the `core` module and passed around everywhere

    Examples
    --------
    >>> from numpydoc.docscrape import FunctionDoc
    >>> from typing import List
    >>>
    >>> # example function
    >>> def add(a:int, b:int):
    ...     """
    ...     Sum of two integers
    ...     """
    ...     return a + b
    >>>
    >>> # create a parser
    >>> class DummyParser(DocParser):
    ...     def to_md_lines(self) -> List[str]:
    ...         return self.lines
    >>>
    >>> # get lines of numpydoc section "Summary"
    >>> doc = FunctionDoc(add)
    >>> lines = doc['Summary']
    >>>
    >>> # parse section "Summary"
    >>> parser = DummyParser(lines=lines)
    >>> parser.to_md_lines()
    ['Sum of two integers']
    '''
    lines:list
    config:Config = dataclassfield(default_factory=lambda: Config())

    @abstractmethod
    def to_md_lines(self) -> List[str]:
        """
        Implement a method that converts the lines (list of str,
        numpydoc.docscrape.Parameter, ... - what's inside the list
        depends on the numpydoc section) defined in the instance
        to markdown.
        """
        pass  # pragma: no cover


@dataclass(frozen=True)
class PyObjParser(ABC):
    '''
    Abstract class for loading a Python object from a string, extracting information from it
    and then outputing this information to Markdown lines using method `to_md_lines`.

    Parameters
    ----------
    obj_namespace
        String pointing to any Python class, function, method, ... or any object
        that has a docstring e.g. "datetime.datetime", "pandas.Timestamp",
        "numpy.array"
    config
        "Global" configuration - parameters that will be used
        in the `core` module and passed around everywhere

    Examples
    --------
    >>> # create a parser
    >>> class DummyParser(PyObjParser):
    ...     def to_md_lines(self):
    ...         return f'**{self.sig_name}**_{inspect.signature(self.obj)}_'
    >>>
    >>> # extract information from given Python object (imported with a string)
    >>> # and convert it to Markdown
    >>> parser = DummyParser(obj_namespace='numpydoc.docscrape.NumpyDocString')
    >>> parser.to_md_lines()
    '**numpydoc.docscrape.NumpyDocString**_(docstring, config=None)_'
    '''
    obj_namespace:str = dataclassfield(default=None)
    config:Config = dataclassfield(default_factory=lambda: Config())
    sig_name:str = dataclassfield(init=False)
    obj:Any = dataclassfield(init=False)

    def __post_init__(self):
        # get Python object
        obj = pydoc.locate(self.obj_namespace)
        # we handle the unlikely case where the user actually was refering to "None"
        if obj is None and self.obj_namespace not in ('builtins.None', 'None'):
            raise NonExistentObjectException(f'Could not load Python object "{self.obj_namespace}"')

        # get name of Python object for the signature
        alias = self.config.alias
        sig_name = alias if alias is not None else self.obj_namespace
        assert isinstance(sig_name, str)

        # because we are in a frozen dataclass we need this workaround to set attributes
        object.__setattr__(self, 'obj', obj)
        object.__setattr__(self, 'sig_name', sig_name)

    @abstractmethod
    def to_md_lines(self, **kwargs) -> List[str]:
        """
        Implement a method that extracts information from given
        python object `obj` (a module, class, class method, function, coroutine, ...)
        such as the signature and converts it to markdown lines.
        """
        pass  # pragma: no cover


# -

# # Parser for pure text sections such as "summary" and "extended summary"

class TextSectionParser(DocParser):
    """
    Parses sections of a numpydoc docstring that contains only
    text (as opposed to for instance the section "Parameters"
    where numpydoc gives us a list of parameters objects).
    """

    def to_md_lines(self) -> List[str]:
        # precision on the expected types inside the list `self.lines`
        self.lines:List[str]
        return self.lines


# # Parser for "Examples" section

# ## Helper to parse a single block

@dataclass(frozen=True)
class ExampleBlockHandler:
    """
    Helper for ExampleParser, converts a single example block in a docstring
    to Markdown lines (see property `markdown_lines`)
    """
    block:ExampleBlock
    config:Config

    @property
    def output_lang(self):
        # output langs indicated directly in examples
        # e.g. {{python}} will override the parameter
        # `examples_md_lang` (as explained in the wiki of the library)
        if self.block.output_lang is None:
            lang:str = self.config.examples_md_lang
            # there should always be a default lang, this cannot be None or such
            assert isinstance(lang, str)
        else:
            lang:str = self.block.output_lang
        return '' if lang == SpecialExampleOutputLanguages.RAW.value else lang

    @staticmethod
    def _text_line_to_md(example_line:ExampleLine) -> List[str]:
        return [example_line.line]

    @staticmethod
    def _output_lang_line_to_md(example_line:ExampleLine) -> List[str]:
        return []

    def _output_line_to_md(self, example_line:ExampleLine) -> List[str]:
        new_lines = []
        # add markdown syntax for begining of code block
        if example_line.global_index == self.block.ix_first_output:
            if self.output_lang != SpecialExampleOutputLanguages.MARKDOWN_RENDERED.value:
                new_lines.append(f'```{self.output_lang}')

        # clean the output line before adding it
        line = example_line.line
        if self.config.remove_doctest_blanklines:
            line = Patterns.blankline.sub(repl='', string=line)
        new_lines.append(line)

        # add markdown syntax for end of code block
        # (note that if there is a single line of output
        #  we will add both beginning and end sign for markdown
        #  code block)
        if example_line.global_index == self.block.ix_last_output:
            if self.output_lang != SpecialExampleOutputLanguages.MARKDOWN_RENDERED.value:
                new_lines.append('```')

        return new_lines

    def _input_line_to_md(self, example_line:ExampleLine) -> List[str]:
        new_lines = []
        # add markdown syntax for begining of code block
        # (same logic as for method `_output_line_to_md`)
        if example_line.global_index == self.block.ix_first_input:
            new_lines.append('```python')

        # clean and then add line
        line = example_line.line
        if self.config.remove_doctest_skip:
            line = Patterns.doctest_skip.sub(repl='', string=line)
        new_lines.append(Patterns.console_py.sub(repl='', string=line))

        # add markdown syntax for end of code block
        if example_line.global_index == self.block.ix_last_input:
            new_lines.append('```')

        return new_lines

    @property
    def markdown_lines(self) -> List[str]:
        transformers = {ExampleLineType.OUTPUT_LANG:self._output_lang_line_to_md,
                        ExampleLineType.TEXT:self._text_line_to_md,
                        ExampleLineType.INPUT:self._input_line_to_md,
                        ExampleLineType.OUTPUT:self._output_line_to_md}
        new_lines = []
        for example_line in self.block.example_lines:
            # get the appropriate function then pass the example line object
            f = transformers[example_line.line_type]
            new_lines.extend(f(example_line=example_line))
        return new_lines


# ## Parser for the full example section

class ExampleParser(DocParser):
    """
    Parses the "Examples" section of a numpydoc docstring
    """

    def to_md_lines(self) -> List[str]:
        # precision on the expected types inside the list `self.lines`
        self.lines:List[str]
        new_lines = []
        blocks:List[ExampleBlock] = ExamplesLabeller(lines=self.lines).example_blocks
        for block in blocks:
            ebh = ExampleBlockHandler(block=block, config=self.config)
            new_lines.extend(ebh.markdown_lines)
        return new_lines


# # Parser for sections similar to `Parameters`

class ParametersLikeSectionParser(DocParser):
    """
    Parses any section of a numpydoc docstring that "behaves"
    like the "Parameters" section e.g. "Other Parameters",
    "Returns", ...

    For these sections numpydoc gives back a list of parameters
    objects (numpydoc.docscrape.Parameter)
    """

    def _param_to_md_lines(self, param:Parameter) -> List[str]:
        new_lines:List[str] = []

        # get name and type and escape them
        name = MdEscaper.escape(param.name).strip()
        name = f'**{name}**' if name != '' else ''
        type_ = param.type.strip()
        type_ = MdEscaper.escape(type_)
        type_ = f"**_{param.type}_** " if param.type != '' else ''
        prefix = '* ' if name != '' or type_ != '' else ''

        # get separator between name and type
        sep_name_type = ' : ' if (name != '' and type_ != '') else ''

        # construct the first line (* {parameter_name} : {parameter_type})
        new_lines.append(f'{prefix}{name}{sep_name_type}{type_}'.strip())

        # get lines of description
        desc_lines = param.desc
        if not len(desc_lines):
            return new_lines

        # if there is a description separate it with a line break
        new_lines.append('')

        # format lines of description
        new_lines.extend(param_description_lines_to_md_lines(desc_lines))
        return new_lines

    def to_md_lines(self) -> List[str]:
        # precision on the expected types inside the list `self.lines`
        self.lines:List[Parameter]
        nb_lines = len(self.lines)
        new_lines = []
        for ix, param in enumerate(self.lines):
            new_lines.extend(self._param_to_md_lines(param))
            # add a line break between parameters. This does
            # not change the rendering but looks prettier
            # when not rendered
            is_last_param = ix == (nb_lines - 1)
            if not is_last_param:
                new_lines.append('')
        return new_lines


# # Parser for "See Also" section

class SeeAlsoParser(DocParser):
    """
    Parses the "See Also" section of a numpydoc docstring
    """

    def to_md_lines(self) -> List[str]:
        # precision on the expected types inside the list `self.lines`
        self.lines:List[Tuple[list, list]]
        nb_lines = len(self.lines)
        new_lines:List[str] = []

        for ix, (funcs, desc_lines) in enumerate(self.lines):
            # example of (funcs, description):
            # ([('example_func2', None), ('example_func3', None)], ['description'])
            # not sure what None could be (second item of each tuple in funcs) ?!

            # add object names
            names = ', '.join(MdEscaper.escape(func[0]).strip() for func in funcs)
            new_lines.append(f"* **{names}**")

            # get description lines
            desc_lines = param_description_lines_to_md_lines(desc_lines)
            if len(desc_lines):
                # if there is a description separate it with a line break
                new_lines.append('')
                new_lines.extend(desc_lines)

            # like with section "Parameters", add a line break between objects
            is_last_param = ix == (nb_lines - 1)
            if not is_last_param:
                new_lines.append('')

        return new_lines


# # Special parsing for the signature

class SignatureParser(PyObjParser):
    """
    Parses the signature of a Python object
    """

    @staticmethod
    def get_signature(obj:Any) -> str:
        """
        Gets the signature of given object as a string.
        This handles the case when the object `obj` is a builtin.

        inspect.signature(self.obj) fails with some builtin objects
        because they are written in C and they cannot be introspected.

        Notes
        -----
        I made this as a staticmethod so it's easier to test with doctest.

        Examples
        --------
        >>> SignatureParser.get_signature(bool)
        '(self, /, *args, **kwargs)'

        >>> from npdoc_to_md import render_string
        >>> SignatureParser.get_signature(render_string)
        '(string: str, ignore_errors: bool = False) -> str'
        """
        assert callable(obj), f'Trying to get signature of non callable object: {obj}'

        try:
            # this will fail for builtins written in C but the except part will handle that
            return str(inspect.signature(obj))
        except ValueError as e:
            if hasattr(obj, '__init__'):
                return str(inspect.signature(obj.__init__))
            else:
                raise SignatureNotFoundException(f'Cannot get signature of object {obj}') from e  # pragma: no cover

    def to_md_lines(self) -> List[str]:
        name = MdEscaper.escape(self.sig_name)
        name_colored = f'<span style="color:purple">{name}</span>'

        # get the level (title, subtitle etc.)
        level = self.config.md_section_level - 1 if self.config.md_section_level > 1 else 1

        # handle case of non callable (e.g. property)
        if not callable(self.obj):
            return [f'{"#" * level} {name_colored}']

        # get signature string and "clean" it (remove self or cls argument)
        sig_str = self.get_signature(obj=self.obj)
        sig_str = MdEscaper.escape(Patterns.self_or_cls.sub(repl='', string=sig_str))
        return [f'{"#" * level} {name_colored}_{sig_str}_']


# # Class to parse every section

# +
class DefaultParsers:
    """
    Parsers for the different sections described in numpydoc style docstrings.

    Attributes
    ----------
    sections : dict[str, DocScraper|PyObjScraper]
        A dictionary with a parser class (values of the dict)
        for each numpydoc section (keys of the dict)
    """
    _parameter_like_sections = ('Returns', 'Yields', 'Parameters', 'Attributes', 'Methods',
                                'Raises', 'Warns', 'Receives', 'Other Parameters')
    _text_sections = ('Summary', 'Extended Summary', 'Notes', 'Warnings', 'References')
    sections = {'Examples':ExampleParser, 'Signature':SignatureParser, 'See Also':SeeAlsoParser}
    sections.update({k:ParametersLikeSectionParser for k in _parameter_like_sections})
    sections.update({k:TextSectionParser for k in _text_sections})


class ParserEngine(PyObjParser):
    """
    Uses the different parsers defined in module npdoc_to_md.parser to convert
    a numpydoc docstring to Markdown
    """

    def section_to_md_lines(self, sections_finder:SectionsFinder, section:str) -> List[str]:
        """
        Converts any `section` of a numpydoc style docstring to markdown lines
        """
        # skip empty sections (except for "Signature" which is done using `inspect.signature`)
        lines = sections_finder[section]
        if section != 'Signature' and not len(lines):
            return []

        # handle bug where a section does not exists and it is still parsed by numpydoc
        # for instance this happened with the section Attributes of pd.DataFrame
        if section not in sections_finder.sections_without_headers and section not in sections_finder.all_visible_sections:
            return []

        # get and instantiate parser class
        parser_class = DefaultParsers.sections.get(section, TextSectionParser)
        if issubclass(parser_class, DocParser):
            parser = parser_class(lines=lines, config=self.config)
        elif issubclass(parser_class, PyObjParser):
            parser = parser_class(obj_namespace=self.obj_namespace, config=self.config)
        else:  # pragma: no cover
            raise TypeError(f'Parser obtained for numpy section "{section}" does not '
                            'subclasss npdoc_to_md.parser.DocParser or '
                            'npdoc_to_md.parser.PyObjParser')
        return parser.to_md_lines()

    def to_md_lines(self) -> List[str]:
        # initialize tool to find sections
        sections_finder = SectionsFinder(self.obj, ignore_custom_section_warning=self.config.ignore_custom_section_warning)
        custom_section_names = list(sections_finder.custom_sections.keys())
        if len(custom_section_names):
            log(f'Found the following custom sections {custom_section_names} in object {self.obj}.\n'
                '(we will interpret these custom sections as markdown text like sections '
                '"Summary" and "Extended Summary")')

        # convert each section in order of appearance to markdown
        new_lines = []
        for section in sections_finder.all_sections:
            new_lines_sublist = self.section_to_md_lines(sections_finder=sections_finder, section=section)
            # after converting if we end up with an empty list we'll skip it
            if not len(new_lines_sublist):
                continue

            # add a header and two line breaks (only one is needed but this is
            # prettier for the non rendered version since you'll have a separation line
            # below the section)
            if section not in sections_finder.sections_without_headers:
                new_lines.append(f'{self.config.md_section_level*"#"} {section}\n\n')

            # add the new lines
            new_lines.append('\n'.join(new_lines_sublist) + '\n\n')
        return new_lines

    def to_md_string(self) -> str:
        """
        Creates a single Markdown string using the output of method
        `to_md_lines`
        """
        return ''.join(self.to_md_lines()).strip()


# -

# # Main function

def parse_and_render(obj_namespace:str, config:Config) -> str:
    """
    Loads object at given namespace (`obj_namespace`)
    e.g. `pandas.DataFrame` and using given configuration
    transforms its docstring to Markdown (optionally
    for desginated members of this object too).
    """
    # case of a single item to parse
    engine = ParserEngine(obj_namespace=obj_namespace, config=config)
    result = engine.to_md_string()
    if config.members is None or len(config.members) == 0:
        return result

    # parse members
    results = [result]
    parsed_members = MembersParser(obj=engine.obj, members=config.members).parsed_members
    for member in parsed_members:

        # we have to make a few changes to the config for members
        config_dict = dataclasses.asdict(config)
        config_dict.pop('members')

        if config_dict['alias'] is not None:
            config_dict['alias'] = f"{config_dict['alias']}.{member}"
        new_config = Config(**config_dict)
        results.append(ParserEngine(obj_namespace=f'{obj_namespace}.{member}', config=new_config).to_md_string())

    return '\n\n'.join(results)
