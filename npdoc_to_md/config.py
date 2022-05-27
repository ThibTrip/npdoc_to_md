"""
Contains configuration objects for functions of this library
as well as placeholders in template files
"""
from dataclasses import dataclass, field as dataclass_field, fields as dataclass_fields, MISSING
from enum import Enum
from typing import get_type_hints, List, Optional

# # Helpers

default_language_examples = 'python'


# ## Enum for special values to designate class members

class MemberFlag(Enum):
    """
    Special values to designate members of a Python object (see parameter `members`
    in the library documentation in the section for placeholders)
    """
    DUNDER = 'dunder$'
    PRIVATE = 'private$'
    PUBLIC = 'public$'


# ## Enum for special values to render examples

class SpecialExampleOutputLanguages(Enum):
    """
    Special ways of representing example outputs in
    a Python's docstring

    Attributes
    ----------
    DEFAULT : str
        Default language for syntax highlighting
        of example output within markdown code block
    RAW : str
        Flag for when we'll use a raw markdown code block
        (no language defined for syntax highlighting)
        for the output of an example
    MARKDOWN_RENDERED : str
        Flag for when we will **not** use a markdown code block
        for the output of an example (e.g. if the user
        wants to have a markdown table as output)
    """
    DEFAULT = default_language_examples
    RAW = 'raw'
    MARKDOWN_RENDERED = 'markdown_rendered'


# # Config class

@dataclass(frozen=True)
class Config:
    """
    Options found throughout the library for how to
    display docstrings in Markdown (see parameters
    for placeholders in the library documentation)
    """
    alias:Optional[str] = None
    examples_md_lang:str = default_language_examples
    remove_doctest_blanklines:bool = False
    remove_doctest_skip:bool = False
    md_section_level:int = 3
    ignore_custom_section_warning:bool = False
    members:List[str] = dataclass_field(default_factory=list)

    def __post_init__(self):
        # verify types
        config_types = get_type_hints(Config)
        for field in dataclass_fields(self):
            attr = field.name
            val = getattr(self, attr)
            type_ = type(val)

            # handle special cases (non primitives e.g. List[str])
            if attr == 'alias':
                if not isinstance(val, str) and val is not None:
                    raise TypeError(f'Parameter "{attr}" is not a str or None. Type: {type_}')
            elif attr == 'members':
                if not isinstance(val, list):
                    raise TypeError(f'Parameter "{attr}" is not a list. Type: {type_}')
                elif any(not isinstance(v, str) for v in val):
                    raise TypeError(f'The parameter "{attr}" (list) contains non strings.')
            # handle normal case
            else:
                expected_type = config_types[attr]
                if not isinstance(val, expected_type):
                    raise TypeError(f'Parameter "{attr}" is not of type {expected_type}. Type: {type_}')

    @staticmethod
    def get_default(field:str):
        """
        Gets the default value of given field of the dataclass.

        Examples
        --------
        >>> Config.get_default('examples_md_lang')
        'python'
        """
        try:
            default = Config.__dataclass_fields__[field].default
            if default is MISSING:  # pragma: no cover
                raise ValueError(f'Field "{field}" has no default value')
            return default
        except KeyError as e:
            raise AttributeError(f'Config has no attribute "{field}"') from e
